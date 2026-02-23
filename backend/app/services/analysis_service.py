from app.services.pdf_service import split_into_clauses, get_contract_type
from app.services.document_service import extract_text_from_document
from app.services.rag_service import search_similar_cases, SAMPLE_CASES
from app.services.korean_law_service import (
    get_relevant_laws,
    search_court_cases,
    check_missing_clauses,
    get_contract_checklist
)
from app.core.openai_client import analyze_clause, generate_alternative_clause


# 면책 조항 문구
DISCLAIMER = """
[면책 조항]
본 분석 결과는 AI 기반 정보 제공 도구로서 법률 자문이 아닙니다.
최종 의사결정은 반드시 법률 전문가와 상담 후 진행하시기 바랍니다.
ContractPilot은 분석 결과의 정확성이나 완전성을 보장하지 않으며,
이를 근거로 한 결정에 대한 책임을 지지 않습니다.
"""


async def analyze_contract(file_bytes: bytes, filename: str = "document.pdf") -> dict:
    """계약서 전체 분석 (PDF, HWP, HWPX 지원)"""
    # 1. 문서에서 텍스트 추출 (파일 형식 자동 감지)
    text = extract_text_from_document(file_bytes, filename)

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
        relevant_laws = []

        if analysis.get("risk_score", 0) >= 6:
            high_risk_count += 1

            # 실제 판례 검색 시도
            try:
                court_cases = await search_court_cases(clause["content"], top_k=2)
                if court_cases:
                    similar_cases = [
                        {
                            "case_number": c.case_number,
                            "summary": c.summary,
                            "court": c.court,
                            "date": c.decision_date,
                            "relevant_text": c.summary
                        }
                        for c in court_cases
                    ]
                else:
                    # API 실패 시 샘플 사용
                    similar_cases = SAMPLE_CASES[:2]
            except Exception:
                similar_cases = SAMPLE_CASES[:2]

            # 관련 법령 조회
            try:
                relevant_laws = await get_relevant_laws(clause["content"], contract_type)
            except Exception:
                relevant_laws = []

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
            "relevant_laws": relevant_laws,
            "alternative": alternative
        })

        total_risk_score += analysis.get("risk_score", 0)

    # 5. 누락 조항 체크
    missing_clauses = check_missing_clauses(contract_type, analyzed_clauses)

    # 6. 체크리스트 조회
    checklist = get_contract_checklist(contract_type)

    # 7. 전체 요약
    avg_risk = total_risk_score / len(clauses) if clauses else 0

    return {
        "contract_type": contract_type,
        "total_clauses": len(clauses),
        "high_risk_clauses": high_risk_count,
        "average_risk_score": round(avg_risk, 1),
        "overall_risk_level": get_overall_risk_level(avg_risk, high_risk_count),
        "clauses": analyzed_clauses,
        "missing_clauses": missing_clauses,
        "checklist": checklist,
        "summary": generate_summary(analyzed_clauses, contract_type, missing_clauses),
        "disclaimer": DISCLAIMER.strip()
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


def generate_summary(
    clauses: list[dict],
    contract_type: str,
    missing_clauses: list[dict] = None
) -> str:
    """분석 요약 생성"""
    high_risk = [c for c in clauses if c["analysis"].get("risk_score", 0) >= 7]
    missing = missing_clauses or []

    summary_parts = []

    # 고위험 조항 요약
    if high_risk:
        issues = []
        for c in high_risk[:3]:
            issues.append(f"- {c['title']}: {c['analysis'].get('summary', '')}")

        summary_parts.append(
            f"이 {contract_type}에서 {len(high_risk)}개의 고위험 조항이 발견되었습니다.\n\n"
            f"주요 문제점:\n{chr(10).join(issues)}"
        )

    # 누락 조항 요약
    if missing:
        missing_items = [f"- {m['clause']} ({m['law']})" for m in missing[:5]]
        summary_parts.append(
            f"\n\n누락된 필수 조항 {len(missing)}개:\n{chr(10).join(missing_items)}"
        )

    if not summary_parts:
        return f"이 {contract_type}는 전반적으로 위험 요소가 적습니다. 일반적인 검토 후 서명을 진행해도 됩니다."

    summary_parts.append("\n\n서명 전 해당 사항들의 검토 및 수정을 권고합니다.")

    return "".join(summary_parts)
