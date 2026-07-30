"""
recommendations.py — Phase 2: AI Prescriptive Recommendation REST API Routes
FastAPI endpoints for fetching prescriptive next-action recommendations and executing one-click case creation / enforcement.
"""
from fastapi import APIRouter, HTTPException, Query

from backend.agents.recommendation_agent import recommendation_agent
from backend.schemas.recommendation import (
    PrescriptiveResponse,
    RecommendationExecuteRequest,
)

router = APIRouter(prefix="/recommendations", tags=["AI Prescriptive Recommendations"])


@router.get("/prescriptive", response_model=PrescriptiveResponse)
async def get_prescriptive_recommendations(
    target_query: str = Query(default="CMF Buds 2a")
):
    """Fetch AI-generated prescriptive next-action recommendations for a product or listing."""
    return recommendation_agent.generate_prescriptive_recommendations(target_query)


@router.post("/execute")
async def execute_recommendation_action(req: RecommendationExecuteRequest):
    """Execute one-click case creation, marketplace takedown, or legal escalation for a recommendation."""
    try:
        return recommendation_agent.execute_recommendation(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
