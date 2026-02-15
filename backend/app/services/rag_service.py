# RAG Service - 판례 검색
# Pinecone은 나중에 연동 예정

# 샘플 판례 데이터 (해커톤용 - 실제로는 벡터 DB에서 검색)
SAMPLE_CASES = [
    {
        "case_number": "대법원 2019다12345",
        "summary": "투자계약에서 일방적 해지권 조항은 신의성실 원칙에 반할 수 있음",
        "court": "대법원",
        "date": "2019-05-15",
        "relevant_text": "투자계약에서 투자자에게만 일방적 해지권을 부여한 조항은 계약 당사자 간 균형을 현저히 해치는 것으로..."
    },
    {
        "case_number": "대법원 2020다67890",
        "summary": "경업금지 조항의 기간과 범위는 합리적으로 제한되어야 함",
        "court": "대법원",
        "date": "2020-08-20",
        "relevant_text": "퇴직 후 경업금지 의무를 부과하는 조항은 그 기간, 지역적 범위, 대상 직종 등이 합리적으로 제한되어야..."
    },
    {
        "case_number": "서울고등법원 2021나11111",
        "summary": "손해배상액 예정 조항이 과다한 경우 감액 가능",
        "court": "서울고등법원",
        "date": "2021-03-10",
        "relevant_text": "계약 위반 시 손해배상액을 예정한 조항이 실제 손해에 비해 현저히 과다한 경우 법원은 이를 감액할 수..."
    },
    {
        "case_number": "대법원 2018다55555",
        "summary": "계약 해제 시 위약금 조항은 민법 제398조에 따라 감액 가능",
        "court": "대법원",
        "date": "2018-11-22",
        "relevant_text": "위약금 약정이 있는 경우에도 그 액수가 부당하게 과다한 경우 법원은 적당히 감액할 수 있다..."
    },
    {
        "case_number": "대법원 2022다33333",
        "summary": "면책조항이 있더라도 고의 또는 중과실에 의한 손해는 면책 불가",
        "court": "대법원",
        "date": "2022-03-17",
        "relevant_text": "계약서에 면책조항이 있더라도 고의 또는 중대한 과실로 인한 손해배상책임은 면제되지 않는다..."
    }
]


async def search_similar_cases(clause: str, top_k: int = 3) -> list[dict]:
    """유사 판례 검색 (현재는 샘플 데이터 반환)"""
    # TODO: Pinecone 연동 시 실제 벡터 검색 구현
    # 현재는 키워드 기반 간단한 매칭

    keywords = {
        "해지": [SAMPLE_CASES[0]],
        "해제": [SAMPLE_CASES[0], SAMPLE_CASES[3]],
        "경업금지": [SAMPLE_CASES[1]],
        "손해배상": [SAMPLE_CASES[2], SAMPLE_CASES[3]],
        "위약금": [SAMPLE_CASES[3]],
        "면책": [SAMPLE_CASES[4]],
        "책임": [SAMPLE_CASES[4]],
    }

    matched = []
    for keyword, cases in keywords.items():
        if keyword in clause:
            for case in cases:
                if case not in matched:
                    matched.append(case)

    return matched[:top_k] if matched else SAMPLE_CASES[:top_k]
