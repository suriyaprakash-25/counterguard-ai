from typing import List, Optional, TypedDict

from backend.types import EvidenceEvent, JSONDict


class InvestigationState(TypedDict):
    """
    Shared state that doubles as the Evidence Timeline.
    This is the single source of truth for the investigation.
    """

    listing_id: str
    listing_data: JSONDict
    evidence_timeline: List[EvidenceEvent]
    agent_findings: JSONDict
    confidence_score: float
    cross_query_count: int
    status: str
    legal_notice_draft: Optional[str]
