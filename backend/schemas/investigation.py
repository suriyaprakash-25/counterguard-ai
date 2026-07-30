from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    listing_url: str
    marketplace: str
    investigation_type: Optional[str] = "Counterfeit Detection"
    planner_strategy: Optional[str] = "Deep Intelligence"
    objectives: List[str] = Field(default_factory=list)
    target_type: Optional[str] = "Marketplace Product URL"
    target_value: Optional[str] = ""
    advanced_options: Optional[Dict[str, Any]] = None


class AnalyzerResult(BaseModel):
    brand: str
    title: str
    price: float
    seller_rating: float
    marketplace: str
    risk_signals: List[str]


class EvidenceResult(BaseModel):
    structured_evidence: Dict[str, Dict[str, str]] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    risk_score: int
    risk_level: str


class InvestigationReport(BaseModel):
    summary: str
    product: str
    marketplace: str
    seller: str
    price: float
    risk_score: int
    risk_level: str
    evidence_summary: Dict[str, Any]
    findings: List[str]
    recommendation: str
    confidence: float
    ai_summary: str = Field(default="")
    ai_reasoning: str = Field(default="")
    investigation_timestamp: str
    recommended_products: List[Dict[str, Any]] = Field(default_factory=list)
    data_confidence_warning: Optional[str] = None

    # Sprint 1 Evidence-Driven Reasoning Fields
    overall_confidence: float = Field(0.85, ge=0.0, le=1.0)
    overall_reasoning: List[str] = Field(default_factory=list)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    conflicting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = Field(default_factory=list)

    # Sprint 1.5 Directed Graph & Progression Fields
    confidence_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_graph: Dict[str, Any] = Field(default_factory=dict)
