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
