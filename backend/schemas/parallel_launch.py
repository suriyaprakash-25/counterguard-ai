"""
Sprint 2.3 — Parallel Investigation Launcher schemas.
Defines request/response types for the /api/v1/discovery/launch endpoint.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CandidateLaunchItem(BaseModel):
    """A single listing candidate submitted for investigation."""

    candidate_id: str
    marketplace: str
    title: str
    url: str
    price: float = 0.0
    seller: str = "Unverified Seller"
    currency: str = "INR"


class ParallelLaunchRequest(BaseModel):
    """
    Request body for POST /api/v1/discovery/launch.
    Accepts a list of selected listing candidates and optional investigation configuration.
    """

    candidates: List[CandidateLaunchItem] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="1–10 listing candidates to investigate concurrently",
    )
    investigation_type: str = Field(
        "Counterfeit Detection", description="Mission type for all investigations"
    )
    planner_strategy: str = Field(
        "Balanced Investigation", description="Planning strategy for all investigations"
    )
    objectives: List[str] = Field(
        default_factory=list, description="Mission objectives (applied to all)"
    )
    priority: str = Field(
        "high", description="Planner priority: low | medium | high | critical"
    )
    notes: Optional[str] = None
    advanced_options: Optional[Dict[str, Any]] = None


class LaunchJobStatus(BaseModel):
    """Status record for a single launched investigation job."""

    candidate_id: str
    investigation_id: str
    marketplace: str
    title: str
    url: str
    status: str  # "pending" | "in_progress" | "completed" | "failed"
    launched_at: str


class ParallelLaunchResponse(BaseModel):
    """
    Response body for POST /api/v1/discovery/launch.
    Returns one LaunchJobStatus per candidate submitted.
    """

    batch_id: str
    total_launched: int
    jobs: List[LaunchJobStatus]
    investigation_ids: List[str]
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BatchStatusResponse(BaseModel):
    """
    Response body for GET /api/v1/discovery/launch/{batch_id}/status.
    Returns live status for each investigation in the batch.
    """

    batch_id: str
    total: int
    completed: int
    in_progress: int
    pending: int
    failed: int
    progress_pct: float
    jobs: List[LaunchJobStatus]
    is_complete: bool
