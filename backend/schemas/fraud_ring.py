"""
fraud_ring.py — Phase 1 & 3: Fraud Ring DTO Schema Definitions
Pydantic models representing detected counterfeit fraud rings, members, shared identifiers, and evidence.
"""
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class FraudRingMember(BaseModel):
    id: str = Field(..., description="Unique member identifier (e.g., seller ID)")
    name: str = Field(..., description="Member display name")
    type: str = Field(default="Seller", description="Entity type")
    marketplace: str = Field(
        default="Unknown", description="Primary marketplace platform"
    )
    risk_score: float = Field(default=80.0, description="Risk threat score (0-100)")
    shared_identifiers: List[str] = Field(
        default_factory=list, description="Shared links (e.g. Phone, GST, Email)"
    )


class FraudRingEvidence(BaseModel):
    id: str = Field(..., description="Evidence ID")
    type: str = Field(
        ..., description="Rule type (e.g. SHARES_PHONE, SHARES_GST, SHARES_WAREHOUSE)"
    )
    description: str = Field(..., description="Detailed explanation of link")
    confidence: float = Field(default=0.90, description="Evidence confidence score")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class FraudRingDetail(BaseModel):
    ring_id: str = Field(..., description="Unique fraud ring cluster ID")
    name: str = Field(..., description="Fraud ring descriptive name")
    threat_level: str = Field(
        ..., description="Threat level: CRITICAL, HIGH, MEDIUM, LOW"
    )
    suspicion_score: float = Field(
        ..., description="Aggregate suspicion threat score (0-100)"
    )
    network_confidence: float = Field(
        default=0.92, description="Network graph confidence score"
    )
    member_count: int = Field(..., description="Total member accounts in ring")
    marketplace_count: int = Field(
        ..., description="Number of distinct marketplaces involved"
    )
    evidence_count: int = Field(..., description="Total supporting evidence nodes")
    shared_identifiers: List[str] = Field(
        default_factory=list, description="Summary of shared identifiers"
    )
    members: List[FraudRingMember] = Field(default_factory=list)
    supporting_evidence: List[FraudRingEvidence] = Field(default_factory=list)
    recommended_action: str = Field(
        ..., description="AI legal takedown / enforcement recommendation"
    )
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class FraudRingListResponse(BaseModel):
    rings: List[FraudRingDetail]
    total_rings: int
    critical_count: int
    meta: Dict[str, Any] = Field(default_factory=dict)
