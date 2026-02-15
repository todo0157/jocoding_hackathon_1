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
