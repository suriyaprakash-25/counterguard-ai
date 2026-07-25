from pydantic import BaseModel
from typing import List, Optional
from backend.types import JSONDict, EvidenceEvent

class InvestigationResponse(BaseModel):
    listing_id: str
    listing_data: JSONDict
    evidence_timeline: List[EvidenceEvent]
    agent_findings: JSONDict
    confidence_score: float
    cross_query_count: int
    status: str
    legal_notice_draft: Optional[str] = None
