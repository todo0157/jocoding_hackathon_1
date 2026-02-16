from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from app.services.analysis_service import analyze_contract
from app.services.chat_service import generate_chat_response
from app.services.docx_generator import generate_safe_contract
from app.services.pdf_report_generator import generate_analysis_report
from app.models.schemas import (
    ContractAnalysisResponse,
    HealthResponse,
    ChatRequest,
    ChatResponse,
    GenerateContractRequest,
    GenerateReportRequest
)

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


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """판례 기반 법률 상담 챗봇"""
    try:
        # conversation_history를 dict 리스트로 변환
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # contract_context를 dict로 변환
        context = None
        if request.contract_context:
            context = {
                "contract_type": request.contract_context.contract_type,
                "high_risk_clauses": request.contract_context.high_risk_clauses,
                "summary": request.contract_context.summary
            }

        result = await generate_chat_response(
            message=request.message,
            conversation_history=history,
            contract_context=context
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/generate-safe-contract")
async def generate_safe_contract_endpoint(request: GenerateContractRequest):
    """수정된 안전한 계약서 Word 파일 생성 및 다운로드"""
    try:
        # Word 문서 생성
        docx_buffer = generate_safe_contract(
            contract_type=request.contract_type,
            clauses=[clause.model_dump() for clause in request.clauses],
            apply_alternatives=request.apply_alternatives
        )

        # 파일명 생성 (한글 URL 인코딩)
        filename = f"{request.contract_type}_modified.docx"
        encoded_filename = quote(filename, safe='')

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Contract generation error: {str(e)}"
        )


@router.post("/generate-report")
async def generate_report_endpoint(request: GenerateReportRequest):
    """분석 리포트 PDF 파일 생성 및 다운로드"""
    try:
        # PDF 리포트 생성
        pdf_buffer = generate_analysis_report(
            contract_type=request.contract_type,
            clauses=[clause.model_dump() for clause in request.clauses],
            summary=request.summary,
            total_clauses=request.total_clauses,
            high_risk_clauses=request.high_risk_clauses,
            average_risk_score=request.average_risk_score,
            overall_risk_level=request.overall_risk_level
        )

        # 파일명 생성 (한글 URL 인코딩)
        filename = f"{request.contract_type}_분석리포트.pdf"
        encoded_filename = quote(filename, safe='')

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers=headers
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Report generation error: {str(e)}"
        )
