import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class EventType(str, Enum):
    NEW_LISTING = "new_listing"
    PRICE_CHANGE = "price_change"
    IMAGE_CHANGE = "image_change"
    DESCRIPTION_CHANGE = "description_change"
    SELLER_CHANGE = "seller_change"
    REVIEW_CHANGE = "review_change"
    INVENTORY_CHANGE = "inventory_change"
    WATCHLIST_TRIGGER = "watchlist_trigger"


class MarketplaceEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: EventType
    marketplace: str
    listing_id: str
    seller_name: str
    data: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


class InvestigationTask(BaseModel):
    agent_name: str
    priority: int = 0
    required_tools: List[str] = Field(default_factory=list)


class PlanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    priority: int = 0
    estimated_cost: float = 0.0
    estimated_runtime_seconds: int = 0
    tasks: List[InvestigationTask] = Field(default_factory=list)
    status: PlanStatus = PlanStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AlertSeverity
    alert_type: str
    reason: str
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_action: str


class WatchlistEntityType(str, Enum):
    SELLER = "seller"
    BRAND = "brand"
    PRODUCT = "product"
    KEYWORD = "keyword"


class WatchlistItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: WatchlistEntityType
    entity_value: str
    watch_reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
