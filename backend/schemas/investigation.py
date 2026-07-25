from typing import Any, Dict, List

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    listing_url: str
    marketplace: str


class AnalyzerResult(BaseModel):
    brand: str
    title: str
    price: float
    seller_rating: float
    marketplace: str
    risk_signals: List[str]


class EvidenceResult(BaseModel):
    price_anomaly: bool
    seller_reputation: str
    listing_quality: str
    missing_warranty: bool
    additional_evidence: Dict[str, Any] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    risk_score: int
    risk_level: str


class InvestigationReport(BaseModel):
    summary: str
    risk_score: int
    risk_level: str
    findings: List[str]
    recommendation: str
