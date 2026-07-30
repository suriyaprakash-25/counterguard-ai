"""
threat_report.py — Phase 1: Executive Threat Intelligence Report DTO Schemas
Pydantic models representing executive-grade Threat Intelligence Reports containing all 11 required sections.
"""
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ThreatIntelligenceReportDTO(BaseModel):
    report_id: str = Field(..., description="Unique report ID")
    product_name: str = Field(..., description="Target product under audit")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    executive_summary: str = Field(
        ..., description="High-level C-level executive summary"
    )
    threat_level: str = Field(
        ..., description="Threat level: CRITICAL, HIGH, MEDIUM, LOW"
    )
    threat_score: float = Field(
        ..., description="Calculated aggregate threat score (0-100)"
    )
    fraud_ring_summary: str = Field(
        ..., description="Detected counterfeit syndicates and clusters"
    )
    historical_similarity: str = Field(
        ..., description="ChromaDB vector memory precedent analysis"
    )
    evidence_summary: List[str] = Field(
        default_factory=list, description="Key physical and digital evidence findings"
    )
    graph_insights: str = Field(
        ...,
        description="Neo4j graph centrality, shared GST, and network topology analysis",
    )
    affected_marketplaces: List[str] = Field(
        default_factory=list, description="List of affected e-commerce channels"
    )
    high_risk_sellers: List[Dict[str, Any]] = Field(
        default_factory=list, description="High-risk merchant directory"
    )
    recommendations: List[string] if False else List[str] = Field(
        default_factory=list, description="Strategic risk mitigation recommendations"
    )
    enforcement_actions: List[str] = Field(
        default_factory=list,
        description="Recommended legal takedown and law enforcement actions",
    )
    coordinator_reasoning: str = Field(
        ..., description="LangGraph coordinator consensus reasoning log"
    )
    meta: Dict[str, Any] = Field(default_factory=dict)


class ThreatReportGenerateRequest(BaseModel):
    product_name: str = Field(
        default="CMF Buds 2a", description="Product under investigation"
    )
    investigation_ids: List[str] = Field(
        default_factory=list, description="Optional investigation IDs to synthesize"
    )
