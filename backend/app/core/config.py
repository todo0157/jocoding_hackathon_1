from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, Literal


class Settings(BaseSettings):
    # App
    app_name: str = "ContractPilot"
    app_env: str = "development"  # development, production
    debug: bool = True

    # CORS 설정
    cors_origins: str = "https://contractpilot.pages.dev,http://localhost:3000"

    @property
    def allowed_origins(self) -> list[str]:
        """환경변수에서 CORS 허용 도메인 목록 반환"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # LLM 제공자 설정
    # "openai" | "upstage" | "anthropic" | "local"
    llm_provider: str = "openai"

    # OpenAI 설정
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-large"

    # Upstage Solar 설정 (한국 로컬 LLM)
    upstage_api_key: Optional[str] = None
    upstage_model: str = "solar-pro"
    upstage_base_url: str = "https://api.upstage.ai/v1/solar"

    # Anthropic Claude 설정
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # 로컬 LLM 설정 (Ollama, vLLM 등)
    local_llm_base_url: str = "http://localhost:11434/v1"
    local_llm_model: str = "llama3.1:8b"

    # 개인정보 보호 설정
    anonymize_personal_data: bool = True  # 개인정보 익명화 활성화
    preserve_amounts_in_anonymization: bool = True  # 금액 정보 보존

    # Pinecone (선택사항)
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "contract-pilot"

    # Database (선택사항)
    database_url: Optional[str] = None

    @property
    def current_api_key(self) -> Optional[str]:
        """현재 선택된 LLM 제공자의 API 키 반환"""
        provider_keys = {
            "openai": self.openai_api_key,
            "upstage": self.upstage_api_key,
            "anthropic": self.anthropic_api_key,
            "local": None,  # 로컬은 API 키 불필요
        }
        return provider_keys.get(self.llm_provider)

    @property
    def current_model(self) -> str:
        """현재 선택된 LLM 제공자의 모델명 반환"""
        provider_models = {
            "openai": self.openai_model,
            "upstage": self.upstage_model,
            "anthropic": self.anthropic_model,
            "local": self.local_llm_model,
        }
        return provider_models.get(self.llm_provider, self.openai_model)

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
