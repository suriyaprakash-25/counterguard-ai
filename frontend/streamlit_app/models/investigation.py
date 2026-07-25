"""
Pydantic models for frontend type-safety and structured access to backend APIs.
Uses modern Pydantic v2 conventions and model validation.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ListingData(BaseModel):
    """Pydantic model representing e-commerce listing attributes."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Item headline title")
    marketplace: str = Field(..., description="Hosting retail platform")
    url: str = Field(..., description="Canonical product address")
    price: str = Field(..., description="Formatted retail pricing string")
    seller: str = Field(..., description="Merchant account handle")
    location: str = Field(..., description="Geographical origin of shipping")
    quantity_sold: int = Field(..., description="Volume of transactions")
    description: str = Field(..., description="Full promotional copy")


class EvidenceEvent(BaseModel):
    """Pydantic model representing atomic actions within an investigation."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: str = Field(..., description="Formatted time of execution")
    agent: str = Field(..., description="Canonical agent designation")
    action: str = Field(..., description="Operation performed")
    detail: str = Field(..., description="Contextual explanation")
    confidence_delta: float = Field(
        ..., description="Incremental confidence score adjustment"
    )


class AgentFinding(BaseModel):
    """Pydantic model representing summary conclusions per agent."""

    model_config = ConfigDict(from_attributes=True)

    finding: str = Field(..., description="Summary anomaly or fact discovered")
    severity: str = Field(..., description="Impact scale classification")


class InvestigationState(BaseModel):
    """Canonical representation of the active investigation across UI views."""

    model_config = ConfigDict(from_attributes=True)

    listing_id: str = Field(..., description="Unique investigation tracking ID")
    listing_data: ListingData = Field(..., description="Item metadata")
    evidence_timeline: List[EvidenceEvent] = Field(
        ..., description="Chronological audit log"
    )
    agent_findings: Dict[str, AgentFinding] = Field(
        ..., description="Mapped conclusions"
    )
    confidence_score: float = Field(..., description="Aggregate anomaly index")
    cross_query_count: int = Field(
        ..., description="Inter-agent collaboration count"
    )
    status: str = Field(..., description="Lifecycle status tag")
    legal_notice_draft: Optional[str] = Field(
        None, description="Draft escalation letter"
    )
