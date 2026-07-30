"""
case_management.py — Phase 1: Collaborative Investigation Workflow DTO Schemas
Pydantic models representing 7 case states, analyst assignments, comments, tags, attachments, and auditable history timelines.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CaseCommentDTO(BaseModel):
    id: str = Field(..., description="Unique comment ID")
    author: str = Field(..., description="Analyst name or agent ID")
    text: str = Field(..., description="Comment text or note")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CaseTimelineEventDTO(BaseModel):
    event_id: str = Field(..., description="Timeline event ID")
    event_type: str = Field(
        ...,
        description="Type: ACTION, RECOMMENDATION, ALERT, REPORT, STATE_CHANGE, COMMENT",
    )
    actor: str = Field(
        ..., description="Actor name (e.g. Lead Analyst, RecommendationAgent)"
    )
    description: str = Field(..., description="Event summary")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CollaborativeCaseDTO(BaseModel):
    id: str = Field(..., description="Unique case ID (e.g. INV-8901)")
    title: str = Field(..., description="Case title")
    product_name: str = Field(..., description="Associated product")
    state: str = Field(
        default="Open",
        description="7 States: Open, Assigned, Investigating, Evidence Collected, Legal Review, Resolved, Closed",
    )
    assignee: str = Field(default="Unassigned", description="Assigned analyst")
    priority: str = Field(
        default="HIGH", description="Priority: CRITICAL, HIGH, MEDIUM, LOW"
    )
    tags: List[str] = Field(default_factory=list)
    comments: List[CaseCommentDTO] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    history_timeline: List[CaseTimelineEventDTO] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    due_date: Optional[str] = Field(
        default=None, description="Target SLA resolution date"
    )


class CaseStateUpdateRequest(BaseModel):
    state: str = Field(
        ...,
        description="New state: Open, Assigned, Investigating, Evidence Collected, Legal Review, Resolved, Closed",
    )
    notes: Optional[str] = Field(default=None, description="Optional transition notes")


class CaseCommentRequest(BaseModel):
    author: str = Field(default="Lead Investigator", description="Author name")
    text: str = Field(..., description="Comment text")


class CaseAssignRequest(BaseModel):
    assignee: str = Field(..., description="Analyst name")
