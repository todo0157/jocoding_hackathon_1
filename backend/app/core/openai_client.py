from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


async def get_embedding(text: str) -> list[float]:
    """텍스트를 벡터 임베딩으로 변환"""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    return response.data[0].embedding


async def analyze_clause(clause: str, context: str = "") -> dict:
    """계약 조항 위험도 분석"""
    system_prompt = """당신은 한국 계약법 전문가입니다.
계약서 조항을 분석하여 위험도를 평가합니다.

응답 형식 (JSON):
{
    "risk_score": 1-10 (10이 가장 위험),
    "risk_level": "low" | "medium" | "high" | "critical",
    "summary": "위험 요약 (1문장)",
    "issues": ["문제점1", "문제점2"],
    "legal_basis": "관련 법조항 또는 판례",
    "suggestion": "수정 제안"
}"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"조항: {clause}\n\n컨텍스트: {context}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    import json
    return json.loads(response.choices[0].message.content)


async def generate_alternative_clause(original: str, issues: list[str]) -> str:
    """수정된 조항 생성"""
    system_prompt = """당신은 한국 계약법 전문가입니다.
문제가 있는 계약 조항을 공정하게 수정합니다.
수정된 조항만 출력하세요."""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"원본 조항:\n{original}\n\n문제점:\n" + "\n".join(issues)}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content
