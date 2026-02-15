from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.analysis_service import analyze_contract
from app.models.schemas import ContractAnalysisResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "version": "0.1.0"}


@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract_endpoint(file: UploadFile = File(...)):
    """계약서 분석 API"""
    # 파일 유효성 검사
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="PDF 파일만 지원됩니다."
        )

    # 파일 크기 제한 (10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="파일 크기가 10MB를 초과합니다."
        )

    try:
        result = await analyze_contract(contents)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/analyze/text")
async def analyze_text_endpoint(text: str):
    """텍스트 직접 분석 (테스트용)"""
    from app.services.pdf_service import split_into_clauses, get_contract_type
    from app.core.openai_client import analyze_clause

    contract_type = get_contract_type(text)
    clauses = split_into_clauses(text)

    results = []
    for clause in clauses[:5]:  # 테스트용 5개 제한
        analysis = await analyze_clause(clause["content"])
        results.append({
            **clause,
            "analysis": analysis
        })

    return {
        "contract_type": contract_type,
        "clauses": results
    }
