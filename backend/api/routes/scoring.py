"""
scoring.py — Phase 2: Hierarchical Intelligence Threat Scoring REST API
FastAPI endpoints providing 8-level entity threat scores and factor explainability logs.
"""
from fastapi import APIRouter, Query

from backend.schemas.scoring import EntityThreatScore, HierarchicalScoreResponse
from backend.services.threat_scoring_engine import threat_scoring_engine

router = APIRouter(prefix="/scoring", tags=["Hierarchical Threat Scoring"])


@router.get("/hierarchical", response_model=HierarchicalScoreResponse)
async def get_hierarchical_threat_scores(
    entity_id: str = Query(default="prod-cmf-buds")
):
    """Fetch 8-level hierarchical threat scores across Listing, Seller, Product, Marketplace, Fraud Ring, Evidence, Investigation, Organization."""
    return threat_scoring_engine.compute_hierarchical_scores(entity_id)


@router.get("/explain/{entity_id}", response_model=EntityThreatScore)
async def explain_entity_threat_score(entity_id: str):
    """Fetch factor-by-factor breakdown and step-by-step explainability logs for a specific entity ID."""
    return threat_scoring_engine.explain_entity_score(entity_id)
