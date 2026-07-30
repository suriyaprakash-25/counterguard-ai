"""
monitoring.py — Phase 1 & 7: Proactive Continuous Monitoring Schemas
Pydantic DTO models representing monitoring jobs, change detection events, execution logs, and API payloads.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MonitoringJobDTO(BaseModel):
    job_id: str = Field(..., description="Unique job ID")
    name: str = Field(..., description="Watchlist or target product name")
    frequency: str = Field(
        default="hourly", description="Run interval: 15m, 30m, hourly, daily"
    )
    status: str = Field(
        default="ACTIVE", description="Job status: ACTIVE, PAUSED, RUNNING, FAILED"
    )
    last_run: Optional[str] = Field(
        default=None, description="ISO timestamp of last execution"
    )
    next_run: Optional[str] = Field(
        default=None, description="ISO timestamp of next scheduled execution"
    )
    total_scans: int = Field(default=0, description="Total completed discovery scans")
    discovered_listings: int = Field(
        default=0, description="Total discovered product listings"
    )
    investigations_triggered: int = Field(
        default=0, description="Total automatically launched investigations"
    )


class ChangeEventDTO(BaseModel):
    event_id: str = Field(..., description="Unique event ID")
    change_type: str = Field(
        ...,
        description="Event type: NEW_LISTING, PRICE_CHANGE, SELLER_CHANGE, REMOVED_LISTING",
    )
    marketplace: str = Field(..., description="E-commerce marketplace")
    product_name: str = Field(..., description="Product title")
    details: str = Field(
        ..., description="Human-readable description of detected change"
    )
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MonitoringHistoryRecordDTO(BaseModel):
    execution_id: str = Field(..., description="Execution ID")
    job_id: str = Field(..., description="Associated job ID")
    job_name: str = Field(..., description="Target name")
    status: str = Field(..., description="Execution status: SUCCESS, FAILED")
    duration_ms: float = Field(..., description="Execution runtime in milliseconds")
    changes_detected: int = Field(..., description="Number of change events detected")
    investigations_launched: int = Field(
        ..., description="Number of auto investigations launched"
    )
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MonitoringStatusResponse(BaseModel):
    server_time: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )
    timezone: str = Field(default="UTC")
    active_jobs: int
    paused_jobs: int
    running_jobs: int
    completed_scans: int
    total_discovered_listings: int
    total_auto_investigations: int
    jobs: List[MonitoringJobDTO]
    recent_events: List[ChangeEventDTO]
