from pydantic import BaseModel
from typing import Optional


class ClauseAnalysis(BaseModel):
    risk_score: int
    risk_level: str
    summary: str
    issues: list[str]
    legal_basis: Optional[str] = None
    suggestion: Optional[str] = None


class SimilarCase(BaseModel):
    case_number: str
    summary: str
    court: str
    date: str
    relevant_text: str


class AnalyzedClause(BaseModel):
    number: int
    title: str
    content: str
    analysis: ClauseAnalysis
    similar_cases: list[SimilarCase]
    alternative: Optional[str] = None


class ContractAnalysisResponse(BaseModel):
    contract_type: str
    total_clauses: int
    high_risk_clauses: int
    average_risk_score: float
    overall_risk_level: str
    clauses: list[AnalyzedClause]
    summary: str
    disclaimer: Optional[str] = None  # 면책 조항


class HealthResponse(BaseModel):
    status: str
    version: str


# Chat 관련 스키마
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ContractContext(BaseModel):
    contract_type: Optional[str] = None
    high_risk_clauses: Optional[list[dict]] = None
    summary: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []
    contract_context: Optional[ContractContext] = None


class CitedCase(BaseModel):
    case_number: str
    summary: str
    relevance: str


class ChatResponse(BaseModel):
    reply: str
    cited_cases: list[CitedCase] = []


# 계약서 생성 관련 스키마
class GenerateContractRequest(BaseModel):
    contract_type: str
    clauses: list[AnalyzedClause]
    apply_alternatives: bool = True


# PDF 리포트 생성 관련 스키마
class GenerateReportRequest(BaseModel):
    contract_type: str
    clauses: list[AnalyzedClause]
    summary: str
    total_clauses: int
    high_risk_clauses: int
    average_risk_score: float
    overall_risk_level: str


# 노동상담 관련 스키마
class LaborConsultationInfo(BaseModel):
    category: Optional[str] = None  # 임금체불, 부당해고, 괴롭힘 등
    employment_status: Optional[str] = None  # 재직중, 퇴사, 해고
    company_size: Optional[str] = None  # 5인미만, 5인이상
    employment_type: Optional[str] = None  # 정규직, 계약직, 프리랜서


class LaborChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []
    consultation_info: Optional[LaborConsultationInfo] = None


class LaborChatResponse(BaseModel):
    reply: str
    cited_cases: list[CitedCase] = []
    needs_expert: bool = False


class ExpertConnectRequest(BaseModel):
    name: str
    phone: str
    preferred_time: str  # morning, afternoon, evening, anytime
    consultation_summary: Optional[str] = None
    agree_privacy: bool = True


# 협업 관련 스키마
class CreateShareRequest(BaseModel):
    analysis_data: dict
    title: Optional[str] = None
    expires_in_days: Optional[int] = None


class AddCollaboratorRequest(BaseModel):
    share_id: str
    user_id: str
    user_name: str
    user_email: str
    permission: str = "view"  # view, comment, edit, admin


class AddCommentRequest(BaseModel):
    share_id: str
    clause_number: int
    content: str
    comment_type: str = "general"  # general, suggestion, question, approval, rejection
    parent_id: Optional[str] = None
    mentions: Optional[list[str]] = None


class ResolveCommentRequest(BaseModel):
    share_id: str
    comment_id: str


class CreateVersionRequest(BaseModel):
    share_id: str
    analysis_data: dict
    description: str
    changes: list[str]


class ShareLinkRequest(BaseModel):
    share_id: str
    permission: str = "view"
    expires_in_hours: int = 24


class UpdatePermissionRequest(BaseModel):
    share_id: str
    user_id: str
    new_permission: str


class RemoveCollaboratorRequest(BaseModel):
    share_id: str
    user_id: str


# 법령 조회 관련 스키마
class LawSearchRequest(BaseModel):
    clause_text: str
    contract_type: str


class ChecklistRequest(BaseModel):
    contract_type: str
    clauses: list[dict]
