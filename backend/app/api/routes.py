from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from app.services.analysis_service import analyze_contract
from app.services.document_service import validate_file, get_supported_formats_message
from app.services.chat_service import generate_chat_response
from app.services.labor_chat_service import generate_labor_chat_response
from app.services.docx_generator import generate_safe_contract
from app.services.pdf_report_generator import generate_analysis_report
from app.models.schemas import (
    ContractAnalysisResponse,
    HealthResponse,
    ChatRequest,
    ChatResponse,
    GenerateContractRequest,
    GenerateReportRequest,
    LaborChatRequest,
    LaborChatResponse,
    ExpertConnectRequest,
    CreateShareRequest,
    AddCollaboratorRequest,
    AddCommentRequest,
    ResolveCommentRequest,
    CreateVersionRequest,
    ShareLinkRequest,
    UpdatePermissionRequest,
    RemoveCollaboratorRequest,
    LawSearchRequest,
    ChecklistRequest,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "version": "0.2.0"}


@router.get("/system/llm-info")
async def get_llm_info():
    """현재 LLM 제공자 정보 조회"""
    from app.core.openai_client import get_current_provider_info
    from app.services.document_service import get_supported_formats_message

    info = get_current_provider_info()
    info["supported_formats"] = get_supported_formats_message()
    return info


@router.post("/system/test-anonymization")
async def test_anonymization(text: str):
    """개인정보 익명화 테스트 (개발용)"""
    from app.services.anonymizer_service import anonymize_text, get_anonymization_stats

    anonymized, mapping = anonymize_text(text, preserve_amounts=True)
    stats = get_anonymization_stats(text)

    return {
        "original_length": len(text),
        "anonymized_length": len(anonymized),
        "anonymized_text": anonymized,
        "stats": stats,
        "mapping_count": len(mapping)
    }


@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract_endpoint(file: UploadFile = File(...)):
    """계약서 분석 API (PDF, HWP, HWPX 지원)"""
    # 파일 내용 읽기
    contents = await file.read()

    # 파일 유효성 검사 (확장자 + 크기)
    is_valid, error_message = validate_file(file.filename, len(contents))
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=error_message
        )

    try:
        result = await analyze_contract(contents, file.filename)
        return result
    except ValueError as e:
        # HWP 파싱 오류 등
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
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


@router.post("/labor-chat", response_model=LaborChatResponse)
async def labor_chat_endpoint(request: LaborChatRequest):
    """노동상담 AI 챗봇"""
    try:
        # conversation_history를 dict 리스트로 변환
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # consultation_info를 dict로 변환
        consultation = None
        if request.consultation_info:
            consultation = {
                "category": request.consultation_info.category,
                "employment_status": request.consultation_info.employment_status,
                "company_size": request.consultation_info.company_size,
                "employment_type": request.consultation_info.employment_type
            }

        result = await generate_labor_chat_response(
            message=request.message,
            conversation_history=history,
            consultation_info=consultation
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"노동상담 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/expert-connect")
async def expert_connect_endpoint(request: ExpertConnectRequest):
    """전문 노무사 상담 연결 신청"""
    try:
        # TODO: 실제 구현 시 DB에 저장하고 알림 발송
        # 현재는 성공 응답만 반환
        return {
            "success": True,
            "message": "상담 신청이 완료되었습니다. 24시간 내에 전문 노무사가 연락드릴 예정입니다.",
            "request_id": f"REQ-{request.phone[-4:]}-001"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"상담 신청 중 오류가 발생했습니다: {str(e)}"
        )


# ==========================================
# 법령 API
# ==========================================

@router.post("/law/search")
async def search_laws(request: LawSearchRequest):
    """관련 법령 검색"""
    from app.services.korean_law_service import get_relevant_laws

    try:
        laws = await get_relevant_laws(request.clause_text, request.contract_type)
        return {"laws": laws, "count": len(laws)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"법령 검색 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/law/cases")
async def search_cases(request: LawSearchRequest):
    """관련 판례 검색"""
    from app.services.korean_law_service import search_court_cases

    try:
        cases = await search_court_cases(request.clause_text)
        return {
            "cases": [
                {
                    "case_number": c.case_number,
                    "case_name": c.case_name,
                    "court": c.court,
                    "decision_date": c.decision_date,
                    "summary": c.summary,
                    "relevance_score": c.relevance_score
                }
                for c in cases
            ],
            "count": len(cases)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"판례 검색 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/law/checklist/{contract_type}")
async def get_checklist(contract_type: str):
    """계약 유형별 필수 조항 체크리스트"""
    from app.services.korean_law_service import get_contract_checklist

    checklist = get_contract_checklist(contract_type)
    return {
        "contract_type": contract_type,
        "checklist": checklist,
        "total_items": len(checklist),
        "required_items": len([c for c in checklist if c.get("required")])
    }


@router.post("/law/check-missing")
async def check_missing_clauses(request: ChecklistRequest):
    """누락된 필수 조항 체크"""
    from app.services.korean_law_service import check_missing_clauses as check_missing

    missing = check_missing(request.contract_type, request.clauses)
    return {
        "contract_type": request.contract_type,
        "missing_clauses": missing,
        "missing_count": len(missing)
    }


# ==========================================
# 협업 API
# ==========================================

@router.post("/collaboration/share")
async def create_share(request: CreateShareRequest):
    """분석 결과 공유 생성"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    # TODO: 실제 인증 시스템에서 사용자 정보 가져오기
    owner_id = "user_" + str(hash(str(request.analysis_data)))[:8]
    owner_name = "사용자"

    try:
        shared = service.create_shared_analysis(
            analysis_data=request.analysis_data,
            owner_id=owner_id,
            owner_name=owner_name,
            title=request.title,
            expires_in_days=request.expires_in_days
        )
        return shared.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"공유 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/collaboration/share/{share_id}")
async def get_share(share_id: str):
    """공유된 분석 조회"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    shared = service.get_shared_analysis(share_id)

    if not shared:
        raise HTTPException(status_code=404, detail="공유된 분석을 찾을 수 없습니다.")

    return shared.to_dict()


@router.post("/collaboration/collaborator")
async def add_collaborator(request: AddCollaboratorRequest):
    """협업자 추가"""
    from app.services.collaboration_service import (
        get_collaboration_service,
        SharePermission
    )

    service = get_collaboration_service()
    # TODO: 실제 인증에서 요청자 ID 가져오기
    added_by = "admin"

    permission_map = {
        "view": SharePermission.VIEW,
        "comment": SharePermission.COMMENT,
        "edit": SharePermission.EDIT,
        "admin": SharePermission.ADMIN,
    }

    permission = permission_map.get(request.permission, SharePermission.VIEW)

    success = service.add_collaborator(
        share_id=request.share_id,
        user_id=request.user_id,
        user_name=request.user_name,
        user_email=request.user_email,
        permission=permission,
        added_by=added_by
    )

    if not success:
        raise HTTPException(status_code=400, detail="협업자 추가에 실패했습니다.")

    return {"success": True, "message": "협업자가 추가되었습니다."}


@router.post("/collaboration/comment")
async def add_comment(request: AddCommentRequest):
    """코멘트 추가"""
    from app.services.collaboration_service import (
        get_collaboration_service,
        CommentType
    )

    service = get_collaboration_service()
    # TODO: 실제 인증에서 사용자 정보 가져오기
    author_id = "user_001"
    author_name = "리뷰어"

    type_map = {
        "general": CommentType.GENERAL,
        "suggestion": CommentType.SUGGESTION,
        "question": CommentType.QUESTION,
        "approval": CommentType.APPROVAL,
        "rejection": CommentType.REJECTION,
    }

    comment = service.add_comment(
        share_id=request.share_id,
        clause_number=request.clause_number,
        author_id=author_id,
        author_name=author_name,
        content=request.content,
        comment_type=type_map.get(request.comment_type, CommentType.GENERAL),
        parent_id=request.parent_id,
        mentions=request.mentions
    )

    if not comment:
        raise HTTPException(status_code=400, detail="코멘트 추가에 실패했습니다.")

    return comment.to_dict()


@router.post("/collaboration/comment/resolve")
async def resolve_comment(request: ResolveCommentRequest):
    """코멘트 해결 처리"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    # TODO: 실제 인증에서 사용자 ID 가져오기
    resolved_by = "user_001"

    success = service.resolve_comment(
        share_id=request.share_id,
        comment_id=request.comment_id,
        resolved_by=resolved_by
    )

    if not success:
        raise HTTPException(status_code=400, detail="코멘트 해결 처리에 실패했습니다.")

    return {"success": True, "message": "코멘트가 해결되었습니다."}


@router.get("/collaboration/comments/{share_id}/{clause_number}")
async def get_comments(share_id: str, clause_number: int):
    """특정 조항의 코멘트 조회"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    comments = service.get_comments_by_clause(share_id, clause_number)

    return {
        "share_id": share_id,
        "clause_number": clause_number,
        "comments": [c.to_dict() for c in comments],
        "count": len(comments)
    }


@router.post("/collaboration/version")
async def create_version(request: CreateVersionRequest):
    """새 버전 생성"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    # TODO: 실제 인증에서 사용자 ID 가져오기
    created_by = "user_001"

    version = service.create_new_version(
        share_id=request.share_id,
        analysis_data=request.analysis_data,
        created_by=created_by,
        description=request.description,
        changes=request.changes
    )

    if not version:
        raise HTTPException(status_code=400, detail="버전 생성에 실패했습니다.")

    return version.to_dict()


@router.get("/collaboration/version/{share_id}/{version_number}")
async def get_version(share_id: str, version_number: int):
    """특정 버전 조회"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    version = service.get_version(share_id, version_number)

    if not version:
        raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")

    return version.to_dict()


@router.get("/collaboration/diff/{share_id}/{v1}/{v2}")
async def get_version_diff(share_id: str, v1: int, v2: int):
    """두 버전 비교"""
    from app.services.collaboration_service import get_collaboration_service

    service = get_collaboration_service()
    diff = service.get_version_diff(share_id, v1, v2)

    if not diff:
        raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")

    return diff


@router.post("/collaboration/share-link")
async def generate_share_link(request: ShareLinkRequest):
    """공유 링크 생성"""
    from app.services.collaboration_service import (
        get_collaboration_service,
        SharePermission
    )

    service = get_collaboration_service()

    permission_map = {
        "view": SharePermission.VIEW,
        "comment": SharePermission.COMMENT,
        "edit": SharePermission.EDIT,
    }

    permission = permission_map.get(request.permission, SharePermission.VIEW)

    link_data = service.generate_share_link(
        share_id=request.share_id,
        permission=permission,
        expires_in_hours=request.expires_in_hours
    )

    if not link_data:
        raise HTTPException(status_code=404, detail="공유를 찾을 수 없습니다.")

    return link_data
