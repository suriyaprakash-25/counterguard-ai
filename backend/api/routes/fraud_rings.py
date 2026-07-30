"""
fraud_rings.py — Phase 5: Fraud Ring REST API Routes
FastAPI endpoints for listing detected counterfeit fraud rings, members, and evidence.
"""
from fastapi import APIRouter, HTTPException

from backend.agents.fraud_ring_agent import fraud_ring_agent
from backend.schemas.fraud_ring import (
    FraudRingDetail,
    FraudRingEvidence,
    FraudRingListResponse,
    FraudRingMember,
)

router = APIRouter(prefix="/threat/rings", tags=["Fraud Ring Intelligence"])


@router.get("", response_model=FraudRingListResponse)
async def list_fraud_rings():
    """Fetch all automatically detected counterfeit fraud rings."""
    return fraud_ring_agent.analyze_graph_for_fraud_rings()


@router.get("/{ring_id}", response_model=FraudRingDetail)
async def get_fraud_ring_detail(ring_id: str):
    """Fetch detailed threat analysis for a specific fraud ring cluster."""
    all_rings = fraud_ring_agent.analyze_graph_for_fraud_rings()
    for ring in all_rings.rings:
        if ring.ring_id == ring_id:
            return ring
    raise HTTPException(status_code=404, detail=f"Fraud Ring '{ring_id}' not found.")


@router.get("/{ring_id}/members", response_model=list[FraudRingMember])
async def get_fraud_ring_members(ring_id: str):
    """Fetch member sellers and accounts operating in a fraud ring."""
    ring = await get_fraud_ring_detail(ring_id)
    return ring.members


@router.get("/{ring_id}/evidence", response_model=list[FraudRingEvidence])
async def get_fraud_ring_evidence(ring_id: str):
    """Fetch supporting graph evidence and shared identifiers for a fraud ring."""
    ring = await get_fraud_ring_detail(ring_id)
    return ring.supporting_evidence
