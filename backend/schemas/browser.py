"""
browser.py — Pydantic schemas for Browser Extension API Communication (POST /api/v1/browser/analyze)
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class BrowserAnalysisRequest(BaseModel):
    """Payload sent by Chrome Extension DOM Extraction Engine."""
    title: str = Field(..., description="Product Title extracted from DOM")
    seller: str = Field("Unverified Seller", description="Seller Name extracted from DOM")
    price: float = Field(0.0, description="Product Price")
    currency: str = Field("INR", description="Currency string")
    url: str = Field(..., description="Product Page URL")
    image: Optional[str] = Field(None, description="Main Product Image URL")
    rating: Optional[float] = Field(None, description="Customer Rating")
    review_count: Optional[int] = Field(None, description="Total Review Count")
    delivery_info: Optional[str] = Field(None, description="Delivery / Shipping details")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Key-value product specifications")
    availability: str = Field("In Stock", description="Stock Availability string")
    brand: Optional[str] = Field(None, description="Brand Name")
    marketplace: str = Field("Amazon", description="Marketplace Name")
    extracted_at: Optional[str] = Field(None, description="Extraction Timestamp")
    confidence_score: float = Field(100.0, description="DOM Extraction confidence score")


class BrowserAnalysisResponse(BaseModel):
    """Response returned by CounterGuard Intelligence Backend to Extension Popup."""
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall Threat Risk Score (0-100)")
    threat_level: str = Field(..., description="CRITICAL | HIGH | MEDIUM | LOW | SAFE")
    seller_trust: float = Field(..., ge=0.0, le=100.0, description="Seller Trust Rating (0-100)")
    recommendation: str = Field(..., description="Actionable Security Recommendation")
    investigation_id: str = Field(..., description="Generated or correlated Investigation ID")
    evidence_id: str = Field(..., description="SHA-256 Evidence Archive ID")
    findings: List[str] = Field(default_factory=list, description="Key Risk Findings & Anomaly Indicators")
    analyzed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
