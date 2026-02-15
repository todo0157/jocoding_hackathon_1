from openai import OpenAI
from app.core.config import get_settings
from app.services.rag_service import search_similar_cases, SAMPLE_CASES

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """당신은 한국 계약법 전문 AI 상담사입니다.

역할:
- 계약서 관련 질문에 친절하고 전문적으로 답변합니다.
- 가능한 경우 관련 판례를 인용하여 설명합니다.
- 법률 자문이 아닌 일반적인 정보 제공임을 명시합니다.

답변 스타일:
- 쉬운 용어로 설명하되 법적 정확성을 유지합니다.
- 핵심 내용을 먼저 말하고 상세 설명을 덧붙입니다.
- 필요시 예시를 들어 설명합니다.

주의사항:
- 확실하지 않은 내용은 추측하지 않습니다.
- 복잡한 사안은 전문 변호사 상담을 권유합니다.
"""


async def generate_chat_response(
    message: str,
    conversation_history: list[dict],
    contract_context: dict = None
) -> dict:
    """챗봇 응답 생성"""

    # 1. 관련 판례 검색
    similar_cases = await search_similar_cases(message, top_k=3)

    # 2. 시스템 프롬프트 구성
    system_content = SYSTEM_PROMPT

    # 계약서 컨텍스트가 있으면 추가
    if contract_context:
        context_info = f"""
현재 사용자가 분석 중인 계약서 정보:
- 계약서 유형: {contract_context.get('contract_type', '알 수 없음')}
- 요약: {contract_context.get('summary', '없음')}
"""
        if contract_context.get('high_risk_clauses'):
            context_info += "\n고위험 조항:\n"
            for clause in contract_context['high_risk_clauses'][:3]:
                context_info += f"- {clause.get('title', '조항')}: {clause.get('summary', '')}\n"

        system_content += f"\n\n{context_info}"

    # 판례 정보 추가
    if similar_cases:
        cases_info = "\n\n참고할 수 있는 관련 판례:\n"
        for case in similar_cases:
            cases_info += f"- {case['case_number']}: {case['summary']}\n"
        system_content += cases_info

    # 3. 메시지 구성
    messages = [{"role": "system", "content": system_content}]

    # 대화 히스토리 추가
    for msg in conversation_history[-10:]:  # 최근 10개만
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    # 현재 메시지 추가
    messages.append({"role": "user", "content": message})

    # 4. OpenAI API 호출
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    reply = response.choices[0].message.content

    # 5. 인용된 판례 추출 (응답에서 언급된 판례만)
    cited_cases = []
    for case in similar_cases:
        if case['case_number'] in reply:
            cited_cases.append({
                "case_number": case['case_number'],
                "summary": case['summary'],
                "relevance": "답변에서 인용됨"
            })

    # 인용된 판례가 없으면 관련 판례 중 상위 2개 제공
    if not cited_cases and similar_cases:
        for case in similar_cases[:2]:
            cited_cases.append({
                "case_number": case['case_number'],
                "summary": case['summary'],
                "relevance": "관련 판례"
            })

    return {
        "reply": reply,
        "cited_cases": cited_cases
    }
