"""
scoring.py — Phase 1: Hierarchical Intelligence Threat Scoring Schemas
Pydantic DTO models representing 8-level entity threat scores, weighted factor contributions, and explainability logs.
"""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class FactorContribution(BaseModel):
    factor_name: str = Field(
        ...,
        description="Scoring factor (e.g., Graph Centrality, Fraud Ring Membership)",
    )
    weight_pct: float = Field(..., description="Factor weight percentage (0-100)")
    raw_score: float = Field(..., description="Raw factor score (0-100)")
    weighted_score: float = Field(..., description="Weighted contribution score")
    description: str = Field(..., description="Human-readable factor explanation")


class EntityThreatScore(BaseModel):
    entity_id: str = Field(..., description="Unique entity ID")
    entity_type: str = Field(
        ...,
        description="Hierarchy level: Listing, Seller, Product, Marketplace, Fraud Ring, Evidence, Investigation, Organization",
    )
    entity_name: str = Field(..., description="Display name")
    threat_score: float = Field(
        ..., description="Calculated aggregate threat score (0-100)"
    )
    threat_level: str = Field(
        ..., description="Threat level: CRITICAL, HIGH, MEDIUM, LOW"
    )
    confidence: float = Field(default=0.90, description="Score confidence score")
    factor_contributions: List[FactorContribution] = Field(default_factory=list)
    reasoning: List[str] = Field(
        default_factory=list, description="Step-by-step explainability logs"
    )
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HierarchicalScoreResponse(BaseModel):
    overall_organization_risk: float = Field(
        ..., description="Top-level organizational threat index"
    )
    hierarchy_scores: Dict[str, EntityThreatScore] = Field(
        ..., description="Map of scores for all 8 entity levels"
    )
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
