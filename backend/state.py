"""
Canonical InvestigationState definition for CounterGuard.
This module serves as the single source of truth for investigation state.
"""

from typing import Dict, List, Optional

from typing_extensions import TypedDict

from backend.models.types import AgentFinding, EvidenceEvent, ListingData


class InvestigationState(TypedDict):
    """
    Shared state that doubles as the Evidence Timeline.
    This is the single source of truth for the investigation.
    """

    listing_id: str
    listing_data: ListingData
    evidence_timeline: List[EvidenceEvent]
    agent_findings: Dict[str, AgentFinding]
    confidence_score: float
    cross_query_count: int
    status: str
    legal_notice_draft: Optional[str]
