"""
threat_graph.py — Phase 1 & 2: Threat Knowledge Graph Schema DTOs
Defines node types, relationship types, and structured response models.
"""
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(
        ..., description="Primary node type label (e.g., Seller, Phone, Listing)"
    )
    name: str = Field(..., description="Display name for graph rendering")
    type: str = Field(..., description="Subtype category")
    confidence: float = Field(
        default=0.85, description="Entity confidence score (0.0 - 1.0)"
    )
    risk_score: float = Field(
        default=50.0, description="Risk threat score (0.0 - 100.0)"
    )
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Custom node properties"
    )


class GraphRelationship(BaseModel):
    id: str = Field(..., description="Unique relationship identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(
        ..., description="Relationship type (e.g., SELLS, SHARES_PHONE, HAS_EVIDENCE)"
    )
    confidence: float = Field(default=0.90, description="Relationship confidence score")
    provenance: str = Field(
        default="Investigation Swarm Audit", description="Origin of link"
    )
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ThreatGraphResponse(BaseModel):
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]
    meta: Dict[str, Any] = Field(default_factory=dict)
