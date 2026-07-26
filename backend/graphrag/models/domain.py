from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RankedEvidence(BaseModel):
    """Historical evidence retrieved and ranked."""

    content: str
    source_investigation_id: str
    relevance_score: float = 0.0
    evidence_type: str = "Unknown"


class PatternMatch(BaseModel):
    """A detected pattern across multiple investigations."""

    pattern_type: str  # e.g., 'repeated_seller', 'repeated_invoice'
    description: str
    frequency: int
    associated_investigation_ids: List[str] = Field(default_factory=list)


class InvestigationIntelligence(BaseModel):
    """
    Unified intelligence layer combining Semantic Retrieval, Graph Intelligence,
    and Structured History.
    """

    similar_cases: List[Dict[str, Any]] = Field(default_factory=list)
    seller_history: Optional[Dict[str, Any]] = None
    graph_network: Dict[str, Any] = Field(default_factory=dict)
    graph_summary: str = ""
    shared_entities: List[str] = Field(default_factory=list)
    historical_evidence: List[RankedEvidence] = Field(default_factory=list)
    repeated_patterns: List[PatternMatch] = Field(default_factory=list)
    network_risk: float = 0.0
    semantic_matches: int = 0
    recommended_focus: List[str] = Field(default_factory=list)
    confidence_score: float = 0.5
