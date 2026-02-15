from app.services.pdf_service import extract_text_from_pdf, split_into_clauses, get_contract_type
from app.services.rag_service import search_similar_cases, SAMPLE_CASES
from app.core.openai_client import analyze_clause, generate_alternative_clause


async def analyze_contract(file_bytes: bytes) -> dict:
    """계약서 전체 분석"""
    # 1. PDF에서 텍스트 추출
    text = extract_text_from_pdf(file_bytes)

    # 2. 계약서 유형 감지
    contract_type = get_contract_type(text)

    # 3. 조항별 분리
    clauses = split_into_clauses(text)

    # 4. 각 조항 분석
    analyzed_clauses = []
    total_risk_score = 0
    high_risk_count = 0

    for clause in clauses:
        # AI 분석
        analysis = await analyze_clause(
            clause["content"],
            context=f"계약서 유형: {contract_type}"
        )

        # 유사 판례 검색 (위험도 높은 경우만)
        similar_cases = []
        if analysis.get("risk_score", 0) >= 6:
            # 실제로는 RAG 검색, 해커톤에서는 샘플 사용
            similar_cases = SAMPLE_CASES[:2]
            high_risk_count += 1

        # 수정안 생성 (위험도 높은 경우)
        alternative = ""
        if analysis.get("risk_score", 0) >= 7:
            alternative = await generate_alternative_clause(
                clause["content"],
                analysis.get("issues", [])
            )

        analyzed_clauses.append({
            **clause,
            "analysis": analysis,
            "similar_cases": similar_cases,
            "alternative": alternative
        })

        total_risk_score += analysis.get("risk_score", 0)

    # 5. 전체 요약
    avg_risk = total_risk_score / len(clauses) if clauses else 0

    return {
        "contract_type": contract_type,
        "total_clauses": len(clauses),
        "high_risk_clauses": high_risk_count,
        "average_risk_score": round(avg_risk, 1),
        "overall_risk_level": get_overall_risk_level(avg_risk, high_risk_count),
        "clauses": analyzed_clauses,
        "summary": generate_summary(analyzed_clauses, contract_type)
    }


def get_overall_risk_level(avg_score: float, high_risk_count: int) -> str:
    """전체 위험 수준 결정"""
    if high_risk_count >= 3 or avg_score >= 7:
        return "critical"
    elif high_risk_count >= 2 or avg_score >= 5:
        return "high"
    elif high_risk_count >= 1 or avg_score >= 3:
        return "medium"
    return "low"


def generate_summary(clauses: list[dict], contract_type: str) -> str:
    """분석 요약 생성"""
    high_risk = [c for c in clauses if c["analysis"].get("risk_score", 0) >= 7]

    if not high_risk:
        return f"이 {contract_type}는 전반적으로 위험 요소가 적습니다. 일반적인 검토 후 서명을 진행해도 됩니다."

    issues = []
    for c in high_risk[:3]:  # 상위 3개만
        issues.append(f"- {c['title']}: {c['analysis'].get('summary', '')}")

    return f"""이 {contract_type}에서 {len(high_risk)}개의 고위험 조항이 발견되었습니다.

주요 문제점:
{chr(10).join(issues)}

서명 전 해당 조항들의 수정을 권고합니다."""
