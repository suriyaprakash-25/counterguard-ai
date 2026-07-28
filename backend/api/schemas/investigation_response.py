from typing import List, Optional

from pydantic import BaseModel

from backend.domain_types import EvidenceEvent, JSONDict


class InvestigationResponse(BaseModel):
    listing_id: str
    listing_data: JSONDict
    evidence_timeline: List[EvidenceEvent]
    agent_findings: JSONDict
    confidence_score: float
    cross_query_count: int
    status: str
    legal_notice_draft: Optional[str] = None
