"""
recommendation.py — Phase 1: AI Prescriptive Recommendation Engine DTO Schemas
Pydantic models representing 8 prescriptive actions, confidence scores, reasoning logs, supporting evidence, graph entities, and precedents.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrustedProductResult(BaseModel):
    product_name: str = Field(default="Official Product")
    official_price: Optional[float] = Field(default=None)
    trusted_domain: Optional[str] = Field(default=None)
    details: Dict[str, Any] = Field(default_factory=dict)


class PrescriptiveRecommendationDTO(BaseModel):
    recommendation_id: str = Field(..., description="Unique recommendation ID")
    action_type: str = Field(
        ...,
        description="Action: INVESTIGATE_IMMEDIATELY, MONITOR, MERGE_CASE, ESCALATE_BRAND, ESCALATE_LEGAL, ISSUE_TAKEDOWN, REQUEST_MANUAL_REVIEW, CLOSE_LOW_RISK",
    )
    title: str = Field(..., description="Action headline")
    confidence: float = Field(..., description="AI confidence score percentage (0-100)")
    urgency: str = Field(..., description="Urgency: CRITICAL, HIGH, MEDIUM, LOW")
    reasoning: List[str] = Field(
        default_factory=list, description="Step-by-step deterministic reasoning log"
    )
    supporting_evidence: List[str] = Field(
        default_factory=list, description="Key physical and digital evidence findings"
    )
    supporting_graph_entities: List[str] = Field(
        default_factory=list,
        description="Associated Neo4j graph nodes (GST, Sellers, Phone)",
    )
    historical_precedents: List[str] = Field(
        default_factory=list, description="ChromaDB vector memory precedent case IDs"
    )
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PrescriptiveResponse(BaseModel):
    target_product: str
    overall_confidence: float
    recommendations: List[PrescriptiveRecommendationDTO]


class RecommendationExecuteRequest(BaseModel):
    recommendation_id: str = Field(..., description="Recommendation ID to execute")
    action_type: str = Field(..., description="Action type")
    notes: Optional[str] = Field(default=None, description="Optional analyst notes")
