"""
watchlist.py — Phase 1 & 2: Watchlist & Alert DTO Schemas
Pydantic models representing 8-entity watchlists, CRUD operations, deduplicated alert events, and notification preferences.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WatchlistItemDTO(BaseModel):
    id: str = Field(..., description="Unique watchlist target ID")
    category: str = Field(
        ...,
        description="Target type: BRAND, PRODUCT, SELLER, PHONE, EMAIL, GST, FRAUD_RING, MARKETPLACE",
    )
    value: str = Field(
        ...,
        description="Target search query or identifier (e.g., GSTIN 07AAAAA0000A1Z5)",
    )
    name: str = Field(..., description="Human-readable title")
    status: str = Field(default="ACTIVE", description="Target status: ACTIVE, PAUSED")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_triggered: Optional[str] = Field(
        default=None, description="ISO timestamp of last alert trigger"
    )
    alert_count: int = Field(default=0, description="Total triggered alerts")
    meta: Dict[str, Any] = Field(default_factory=dict)


class WatchlistCreateRequest(BaseModel):
    category: str = Field(
        ...,
        description="Target type: BRAND, PRODUCT, SELLER, PHONE, EMAIL, GST, FRAUD_RING, MARKETPLACE",
    )
    value: str = Field(..., description="Target search query or identifier")
    name: str = Field(..., description="Human-readable title")


class AlertEventDTO(BaseModel):
    alert_id: str = Field(..., description="Unique alert ID")
    watchlist_id: Optional[str] = Field(
        default=None, description="Associated watchlist ID"
    )
    event_type: str = Field(
        ...,
        description="Event: NEW_LISTING, PRICE_ANOMALY, RING_GROWTH, SELLER_REAPPEARS, VECTOR_MATCH, THREAT_SCORE_SURGE, CASE_COMPLETE",
    )
    severity: str = Field(
        ..., description="Severity level: CRITICAL, HIGH, MEDIUM, LOW"
    )
    title: str = Field(..., description="Alert headline")
    description: str = Field(..., description="Detailed alert summary")
    marketplace: Optional[str] = Field(default=None, description="Marketplace platform")
    investigation_id: Optional[str] = Field(
        default=None, description="Linked investigation case ID"
    )
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_read: bool = Field(default=False, description="Read state")


class WebhookTestRequest(BaseModel):
    target_url: str = Field(
        default="https://api.counterguard.ai/v1/webhooks/alerts",
        description="Destination webhook URL",
    )
