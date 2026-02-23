"""
계약서 분석용 AI 클라이언트
다중 LLM 제공자 지원 + 개인정보 익명화
"""
import json
from typing import List, Dict, Optional

from app.core.config import get_settings
from app.core.llm_client import SecureLLMClient, get_provider_info


settings = get_settings()

# 보안 LLM 클라이언트 (개인정보 익명화 적용)
_secure_client: Optional[SecureLLMClient] = None


def _get_client() -> SecureLLMClient:
    """싱글톤 클라이언트 반환"""
    global _secure_client
    if _secure_client is None:
        _secure_client = SecureLLMClient()
    return _secure_client


async def get_embedding(text: str) -> List[float]:
    """텍스트를 벡터 임베딩으로 변환 (개인정보 익명화 적용)"""
    client = _get_client()
    return await client.get_embedding(text)


async def analyze_clause(clause: str, context: str = "") -> dict:
    """
    계약 조항 위험도 분석
    - 개인정보 자동 익명화 후 분석
    - 다중 LLM 제공자 지원
    """
    system_prompt = """당신은 한국 계약법 전문가입니다.
계약서 조항을 분석하여 위험도를 평가합니다.

주의사항:
- 개인정보가 마스킹된 형태로 제공될 수 있습니다 (예: 홍**, ***-****-1234)
- 마스킹된 정보는 그대로 유지하면서 분석해주세요.

응답 형식 (JSON):
{
    "risk_score": 1-10 (10이 가장 위험),
    "risk_level": "low" | "medium" | "high" | "critical",
    "summary": "위험 요약 (1문장)",
    "issues": ["문제점1", "문제점2"],
    "legal_basis": "관련 법조항 또는 판례",
    "suggestion": "수정 제안"
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"조항: {clause}\n\n컨텍스트: {context}"}
    ]

    client = _get_client()
    response = await client.chat_completion(
        messages=messages,
        temperature=0.3,
        json_response=True
    )

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 기본값 반환
        return {
            "risk_score": 5,
            "risk_level": "medium",
            "summary": "분석 결과를 파싱할 수 없습니다.",
            "issues": ["분석 재시도가 필요합니다."],
            "legal_basis": "",
            "suggestion": ""
        }


async def generate_alternative_clause(original: str, issues: List[str]) -> str:
    """
    수정된 조항 생성
    - 개인정보 자동 익명화 후 생성
    """
    system_prompt = """당신은 한국 계약법 전문가입니다.
문제가 있는 계약 조항을 공정하게 수정합니다.

주의사항:
- 개인정보가 마스킹된 형태로 제공될 수 있습니다
- 마스킹된 정보는 그대로 유지하면서 수정해주세요
- 수정된 조항만 출력하세요"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"원본 조항:\n{original}\n\n문제점:\n" + "\n".join(issues)}
    ]

    client = _get_client()
    return await client.chat_completion(
        messages=messages,
        temperature=0.5,
        json_response=False
    )


async def analyze_with_context(
    clause: str,
    context: str = "",
    similar_cases: Optional[List[Dict]] = None
) -> dict:
    """
    판례 컨텍스트를 포함한 심층 분석
    """
    system_prompt = """당신은 한국 계약법 전문가입니다.
계약서 조항을 분석하고 관련 판례를 참고하여 위험도를 평가합니다.

응답 형식 (JSON):
{
    "risk_score": 1-10,
    "risk_level": "low" | "medium" | "high" | "critical",
    "summary": "위험 요약",
    "issues": ["문제점 목록"],
    "legal_basis": "관련 법조항",
    "related_cases": ["관련 판례 분석"],
    "suggestion": "수정 제안",
    "confidence": 0.0-1.0
}"""

    user_content = f"조항: {clause}\n\n컨텍스트: {context}"

    if similar_cases:
        case_text = "\n\n관련 판례:\n"
        for case in similar_cases[:3]:  # 최대 3개 판례
            case_text += f"- {case.get('case_number', '')}: {case.get('summary', '')}\n"
        user_content += case_text

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    client = _get_client()
    response = await client.chat_completion(
        messages=messages,
        temperature=0.3,
        json_response=True
    )

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return await analyze_clause(clause, context)


def get_current_provider_info() -> Dict:
    """현재 사용 중인 LLM 제공자 정보"""
    return get_provider_info()
