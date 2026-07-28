from datetime import datetime
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.schemas.investigation import InvestigationReport


class InvestigationHistoryItem(BaseModel):
    """
    Lightweight summary representation of an investigation record for listing.
    """

    id: str
    listing_url: str
    marketplace: str
    status: str
    created_at: str
    updated_at: str
    product: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


class InvestigationListResponse(BaseModel):
    """
    Paginated list of investigation history records.
    """

    items: List[InvestigationHistoryItem] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    model_config = ConfigDict(from_attributes=True)


class EvidenceItemSchema(BaseModel):
    """
    Pydantic schema representing a timeline evidence event from specialist agents.
    """

    id: str
    agent: str
    action: str
    detail: str
    confidence_delta: float = 0.0
    timestamp: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_ev_timestamp(cls, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


class InvestigationDetailResponse(BaseModel):
    """
    Detailed investigation response including full assessment report, evidence timeline, and enriched intelligence fields.
    """

    id: str
    listing_url: str
    marketplace: str
    status: str
    created_at: str
    updated_at: str
    report: Optional[InvestigationReport] = None
    evidence_timeline: List[EvidenceItemSchema] = Field(default_factory=list)

    # Enriched Cyber Intelligence Dashboard fields
    evidence: Optional[List[Dict[str, Any]]] = None
    consensus: Optional[Dict[str, Any]] = None
    memory_context: Optional[Dict[str, Any]] = None
    agent_activity: Optional[List[Dict[str, Any]]] = None
    recommended_products: Optional[List[Dict[str, Any]]] = None
    product_comparison: Optional[Dict[str, Any]] = None
    price_intelligence: Optional[Dict[str, Any]] = None
    recommendation_summary: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


class DeleteInvestigationResponse(BaseModel):
    """
    Confirmation response schema upon successful deletion of an investigation record.
    """

    id: str
    message: str
    success: bool = True
