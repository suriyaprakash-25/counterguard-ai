"""
Sprint 2.5 — Product Intelligence Report Schemas

Defines types for aggregated multi-investigation Product Intelligence Reports.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ListingReportItem(BaseModel):
    """Individual listing investigation details inside a product report."""

    investigation_id: str
    marketplace: str
    listing_url: str
    title: str
    seller: str
    price: float
    risk_score: float
    verdict: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    confidence: float
    evidence_count: int
    top_risk_factor: Optional[str] = None
    last_updated: str


class ProductIntelligenceReportRequest(BaseModel):
    """Request payload to generate a Product Intelligence Report from investigation IDs."""

    investigation_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of 1-20 completed investigation IDs to aggregate into a report",
    )
    product_name: Optional[str] = Field(
        None, description="Optional canonical product name for the report title"
    )


class ProductIntelligenceReport(BaseModel):
    """
    Sprint 2.5 Aggregated Product Intelligence Report.
    Synthesizes findings across multiple marketplace investigations for a single product.
    """

    report_id: str
    product_name: str
    generated_at: str
    total_listings: int
    safe_listings: int
    suspicious_listings: int
    overall_product_risk: float = Field(
        ..., description="Aggregated risk score (0-100)"
    )
    overall_risk_level: str = Field(..., description="LOW | MEDIUM | HIGH | CRITICAL")
    highest_risk_marketplace: str
    recommended_seller: Optional[str] = None
    marketplace_distribution: Dict[str, int] = Field(default_factory=dict)
    evidence_summary: List[str] = Field(default_factory=list)
    coordinator_summary: str
    investigations: List[ListingReportItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
