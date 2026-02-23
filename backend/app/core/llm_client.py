"""
통합 LLM 클라이언트
OpenAI, Upstage Solar, Anthropic Claude, 로컬 LLM 지원
개인정보보호법 준수를 위한 익명화 기능 내장
"""
import json
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from app.core.config import get_settings
from app.services.anonymizer_service import anonymize_text, restore_text


settings = get_settings()


class BaseLLMClient(ABC):
    """LLM 클라이언트 기본 클래스"""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_response: bool = False
    ) -> str:
        """채팅 완료 API 호출"""
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """텍스트 임베딩 생성"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT 클라이언트"""

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_response: bool = False
    ) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_response:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    async def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=settings.embedding_model,
            input=text
        )
        return response.data[0].embedding


class UpstageClient(BaseLLMClient):
    """Upstage Solar 클라이언트 (한국 로컬 LLM)"""

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=settings.upstage_api_key,
            base_url=settings.upstage_base_url
        )
        self.model = settings.upstage_model

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_response: bool = False
    ) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        # Upstage는 JSON 모드 지원 여부 확인 필요
        if json_response:
            # JSON 형식 요청을 시스템 프롬프트에 포함
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n\n응답은 반드시 유효한 JSON 형식으로 해주세요."

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    async def get_embedding(self, text: str) -> List[float]:
        # Upstage 임베딩 API 사용
        response = self.client.embeddings.create(
            model="solar-embedding-1-large",
            input=text
        )
        return response.data[0].embedding


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude 클라이언트"""

    def __init__(self):
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
        except ImportError:
            raise ImportError("anthropic 패키지가 필요합니다. pip install anthropic")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_response: bool = False
    ) -> str:
        # Claude API는 system 메시지를 별도 파라미터로 받음
        system_message = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
                if json_response:
                    system_message += "\n\n응답은 반드시 유효한 JSON 형식으로 해주세요."
            else:
                chat_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_message,
            messages=chat_messages,
            temperature=temperature,
        )
        return response.content[0].text

    async def get_embedding(self, text: str) -> List[float]:
        # Claude는 임베딩 API 없음, OpenAI 폴백
        fallback = OpenAIClient()
        return await fallback.get_embedding(text)


class LocalLLMClient(BaseLLMClient):
    """로컬 LLM 클라이언트 (Ollama, vLLM 등)"""

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(
            api_key="ollama",  # 로컬은 더미 키
            base_url=settings.local_llm_base_url
        )
        self.model = settings.local_llm_model

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_response: bool = False
    ) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if json_response:
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n\n응답은 반드시 유효한 JSON 형식으로 해주세요."

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    async def get_embedding(self, text: str) -> List[float]:
        # Ollama 임베딩
        response = self.client.embeddings.create(
            model="nomic-embed-text",
            input=text
        )
        return response.data[0].embedding


class LLMClientFactory:
    """LLM 클라이언트 팩토리"""

    _clients: Dict[str, BaseLLMClient] = {}

    @classmethod
    def get_client(cls, provider: Optional[str] = None) -> BaseLLMClient:
        """LLM 클라이언트 인스턴스 반환 (싱글톤)"""
        provider = provider or settings.llm_provider

        if provider not in cls._clients:
            cls._clients[provider] = cls._create_client(provider)

        return cls._clients[provider]

    @classmethod
    def _create_client(cls, provider: str) -> BaseLLMClient:
        """LLM 클라이언트 생성"""
        clients = {
            "openai": OpenAIClient,
            "upstage": UpstageClient,
            "anthropic": AnthropicClient,
            "local": LocalLLMClient,
        }

        if provider not in clients:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")

        return clients[provider]()


# 개인정보 익명화가 적용된 LLM 호출 래퍼
class SecureLLMClient:
    """개인정보 보호 기능이 내장된 LLM 클라이언트"""

    def __init__(self, provider: Optional[str] = None):
        self.client = LLMClientFactory.get_client(provider)
        self.anonymize = settings.anonymize_personal_data
        self.preserve_amounts = settings.preserve_amounts_in_anonymization

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        json_response: bool = False,
        skip_anonymization: bool = False
    ) -> str:
        """
        개인정보 익명화 후 LLM 호출

        Args:
            messages: 메시지 목록
            temperature: 생성 온도
            json_response: JSON 응답 요청
            skip_anonymization: 익명화 건너뛰기

        Returns:
            LLM 응답 텍스트
        """
        mappings = []

        # 익명화 적용
        if self.anonymize and not skip_anonymization:
            processed_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    anonymized, mapping = anonymize_text(
                        msg["content"],
                        preserve_amounts=self.preserve_amounts
                    )
                    mappings.append(mapping)
                    processed_messages.append({
                        "role": msg["role"],
                        "content": anonymized
                    })
                else:
                    processed_messages.append(msg)
            messages = processed_messages

        # LLM 호출
        response = await self.client.chat_completion(
            messages, temperature, json_response
        )

        return response

    async def get_embedding(self, text: str, skip_anonymization: bool = False) -> List[float]:
        """개인정보 익명화 후 임베딩 생성"""
        if self.anonymize and not skip_anonymization:
            text, _ = anonymize_text(text, preserve_amounts=self.preserve_amounts)

        return await self.client.get_embedding(text)


# 기본 클라이언트 인스턴스
def get_llm_client(secure: bool = True) -> BaseLLMClient | SecureLLMClient:
    """LLM 클라이언트 가져오기"""
    if secure:
        return SecureLLMClient()
    return LLMClientFactory.get_client()


def get_provider_info() -> Dict[str, Any]:
    """현재 LLM 제공자 정보 반환"""
    return {
        "provider": settings.llm_provider,
        "model": settings.current_model,
        "anonymization_enabled": settings.anonymize_personal_data,
        "preserve_amounts": settings.preserve_amounts_in_anonymization,
    }
