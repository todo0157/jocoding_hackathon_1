# 노동상담 챗봇 서비스
from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

LABOR_SYSTEM_PROMPT = """# 역할
당신은 대한민국 노동법 전문 AI 상담사 "노동톡"입니다.
근로자의 노동 관련 고민을 듣고, 상황을 분석하여 적절한 조언을 제공합니다.

# 핵심 원칙
1. **공감 우선**: 힘든 상황에 처한 근로자의 마음을 먼저 헤아립니다
2. **정확한 정보**: 근로기준법, 노동관계법령에 근거한 정보만 제공합니다
3. **실용적 조언**: 실제로 실행 가능한 구체적인 해결 방법을 안내합니다
4. **한계 인식**: AI의 한계를 인정하고, 필요시 전문 노무사 상담을 권유합니다

# 상담 진행 순서

## 1단계: 상황 파악 (필수 정보 수집)
다음 정보를 자연스러운 대화로 파악하세요:
- 현재 고용 상태 (재직 중 / 퇴사 / 해고)
- 근무 기간
- 회사 규모 (5인 미만 / 5인 이상)
- 고용 형태 (정규직 / 계약직 / 일용직 / 프리랜서)
- 구체적인 문제 상황

## 2단계: 문제 분류
상담 내용을 다음 카테고리로 분류하세요:
- 임금체불 (월급, 수당, 퇴직금 미지급)
- 부당해고 (해고 통보, 권고사직 강요)
- 직장 내 괴롭힘 (폭언, 따돌림, 부당 업무지시)
- 산업재해 (업무상 부상, 질병)
- 근로조건 (연차, 휴가, 근로시간, 휴게시간)
- 4대보험 (미가입, 체납)
- 기타

## 3단계: 법률 정보 제공
해당 상황에 적용되는 법률 조항을 안내하세요:
- 관련 법률 및 조항 (예: 근로기준법 제36조)
- 근로자의 권리
- 회사의 의무
- 위반 시 처벌 규정

## 4단계: 해결 방법 안내
단계별 해결 방법을 제시하세요:
1. 스스로 할 수 있는 것 (증거 수집, 내용증명 등)
2. 무료 구제 기관 (고용노동부, 노동위원회 등)
3. 전문가 도움이 필요한 경우

## 5단계: 전문가 연결 제안
다음 상황에서는 노무사 상담을 적극 권유하세요:
- 금액이 큰 경우 (임금체불 300만원 이상, 퇴직금 등)
- 법적 절차가 필요한 경우 (진정, 소송)
- 회사가 대응하지 않는 경우
- 복잡한 사안 (여러 문제가 얽힌 경우)
- 시급한 경우 (해고 예정, 시효 임박)

전문가 연결 권유 시 다음 문구를 사용하세요:
"이 사안은 전문 노무사의 도움을 받으시면 더 확실하게 해결하실 수 있어요. 전문 노무사 무료 상담 연결을 도와드릴까요?"

# 주요 상담 유형별 가이드

## 임금체불
필수 확인: 체불 금액, 기간, 근로계약서, 급여명세서
안내: 임금채권 소멸시효 3년, 고용노동부 진정, 체당금 제도, 지연이자 연 20%

## 부당해고
필수 확인: 해고 통보 방식, 해고 사유, 근속 기간, 5인 이상 여부
안내: 해고예고수당 30일분, 부당해고 구제신청 (3개월 내)

## 직장 내 괴롭힘
필수 확인: 구체적 행위, 기간/빈도, 증거, 회사 신고 여부
안내: 근로기준법 제76조의2, 회사 내 신고, 고용노동부 신고

## 산업재해
필수 확인: 재해 상황, 부상/질병 내용, 치료 현황, 산재보험 가입
안내: 산재 신청 절차, 요양급여, 휴업급여, 장해급여

# 응답 스타일
- 친근하고 따뜻한 말투 ("~해요", "~드릴게요")
- 이모지 적절히 사용 (과하지 않게)
- 긴 설명은 bullet point로 정리
- 한 번에 너무 많은 정보 X
- 대화 이어갈 질문으로 마무리

# 주의사항
1. 법적 판단 단정 X ("~입니다" → "~로 보입니다", "~가능성이 높습니다")
2. 소송 결과 예측 X
3. 회사 직접 비난 X
4. 감정적 조언 (복수, 폭로 등) X
5. 5인 미만 사업장 근로기준법 적용 제외 사항 정확히 안내"""

# 노동법 관련 샘플 판례
LABOR_SAMPLE_CASES = [
    {
        "case_number": "대법원 2020다12345",
        "summary": "해고예고 없이 즉시 해고한 경우 30일분 통상임금을 해고예고수당으로 지급해야 함",
        "court": "대법원",
        "date": "2020-03-15",
        "keywords": ["해고", "해고예고", "해고예고수당", "즉시해고"]
    },
    {
        "case_number": "대법원 2019다67890",
        "summary": "정당한 이유 없는 해고는 부당해고로서 무효이며, 근로자는 원직복직 및 해고기간 임금 청구 가능",
        "court": "대법원",
        "date": "2019-08-20",
        "keywords": ["부당해고", "해고", "원직복직", "권고사직"]
    },
    {
        "case_number": "대법원 2021다11111",
        "summary": "임금체불에 대해 퇴직일로부터 14일 이내 미지급 시 연 20% 지연이자 발생",
        "court": "대법원",
        "date": "2021-05-10",
        "keywords": ["임금체불", "임금", "월급", "지연이자", "퇴직금"]
    },
    {
        "case_number": "서울고등법원 2022나22222",
        "summary": "직장 내 괴롭힘에 해당하는 행위로 인한 정신적 손해에 대해 사용자 배상책임 인정",
        "court": "서울고등법원",
        "date": "2022-07-15",
        "keywords": ["괴롭힘", "폭언", "갑질", "따돌림", "정신적손해"]
    },
    {
        "case_number": "대법원 2018다33333",
        "summary": "근로계약서 미작성 시에도 실질적 근로관계가 인정되면 근로기준법상 보호 적용",
        "court": "대법원",
        "date": "2018-11-22",
        "keywords": ["근로계약서", "근로관계", "프리랜서", "특수고용"]
    },
    {
        "case_number": "대법원 2020다44444",
        "summary": "연차휴가 미사용 수당은 퇴직 시 정산하여 지급해야 함",
        "court": "대법원",
        "date": "2020-09-30",
        "keywords": ["연차", "휴가", "연차수당", "미사용연차"]
    },
    {
        "case_number": "대법원 2019다55555",
        "summary": "업무상 재해로 인한 부상은 산재보험으로 보상받을 권리가 있음",
        "court": "대법원",
        "date": "2019-04-25",
        "keywords": ["산재", "산업재해", "업무상재해", "부상", "치료"]
    },
    {
        "case_number": "서울행정법원 2021구합66666",
        "summary": "5인 미만 사업장도 임금체불, 퇴직금, 최저임금 규정은 적용됨",
        "court": "서울행정법원",
        "date": "2021-12-10",
        "keywords": ["5인미만", "소규모", "퇴직금", "최저임금"]
    }
]


async def search_labor_cases(message: str, top_k: int = 3) -> list[dict]:
    """노동 관련 판례 검색 (키워드 기반)"""
    matched = []
    message_lower = message.lower()

    for case in LABOR_SAMPLE_CASES:
        for keyword in case["keywords"]:
            if keyword in message_lower or keyword in message:
                if case not in matched:
                    matched.append(case)
                    break

    return matched[:top_k] if matched else LABOR_SAMPLE_CASES[:2]


async def generate_labor_chat_response(
    message: str,
    conversation_history: list[dict],
    consultation_info: dict = None
) -> dict:
    """노동상담 챗봇 응답 생성"""

    # 1. 관련 판례 검색
    similar_cases = await search_labor_cases(message, top_k=3)

    # 2. 시스템 프롬프트 구성
    system_content = LABOR_SYSTEM_PROMPT

    # 상담 정보가 있으면 추가
    if consultation_info:
        context_info = "\n\n현재 상담 정보:\n"
        if consultation_info.get('category'):
            context_info += f"- 상담 유형: {consultation_info['category']}\n"
        if consultation_info.get('employment_status'):
            context_info += f"- 고용 상태: {consultation_info['employment_status']}\n"
        if consultation_info.get('company_size'):
            context_info += f"- 회사 규모: {consultation_info['company_size']}\n"
        system_content += context_info

    # 판례 정보 추가
    if similar_cases:
        cases_info = "\n\n참고할 수 있는 관련 판례:\n"
        for case in similar_cases:
            cases_info += f"- {case['case_number']}: {case['summary']}\n"
        system_content += cases_info

    # 3. 메시지 구성
    messages = [{"role": "system", "content": system_content}]

    # 대화 히스토리 추가 (최근 10개)
    for msg in conversation_history[-10:]:
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

    # 5. 인용된 판례 추출
    cited_cases = []
    for case in similar_cases:
        if case['case_number'] in reply:
            cited_cases.append({
                "case_number": case['case_number'],
                "summary": case['summary'],
                "relevance": "답변에서 인용됨"
            })

    # 인용된 판례가 없으면 관련 판례 상위 2개
    if not cited_cases and similar_cases:
        for case in similar_cases[:2]:
            cited_cases.append({
                "case_number": case['case_number'],
                "summary": case['summary'],
                "relevance": "관련 판례"
            })

    # 6. 전문가 연결 필요 여부 판단
    needs_expert = any(keyword in message.lower() for keyword in [
        "소송", "진정", "고소", "신고", "얼마", "받을 수 있", "청구",
        "퇴직금", "해고", "체불", "300만원", "500만원", "1000만원"
    ])

    return {
        "reply": reply,
        "cited_cases": cited_cases,
        "needs_expert": needs_expert
    }
