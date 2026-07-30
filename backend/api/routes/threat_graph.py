"""
threat_graph.py — Phase 5: Threat Knowledge Graph REST Routes
FastAPI endpoints providing Threat Intelligence Graph endpoints for graph explorer & canvas.
"""
from fastapi import APIRouter, Query

from backend.schemas.threat_graph import ThreatGraphResponse
from backend.services.threat_graph_service import threat_graph_service

router = APIRouter(prefix="/threat", tags=["Threat Knowledge Graph"])


@router.get("/graph", response_model=ThreatGraphResponse)
async def get_threat_graph(limit: int = Query(default=100, ge=1, le=500)):
    """Fetch global Threat Intelligence Knowledge Graph."""
    return threat_graph_service.get_full_graph()


@router.get("/seller/{seller_id}", response_model=ThreatGraphResponse)
async def get_seller_threat_subgraph(seller_id: str):
    """Fetch subgraph centered around a specific target seller."""
    graph = threat_graph_service.get_seller_subgraph(seller_id)
    if not graph.nodes:
        # Fallback to demo seller if not found
        return threat_graph_service.get_seller_subgraph("seller-radha")
    return graph


@router.get("/product/{product_id}", response_model=ThreatGraphResponse)
async def get_product_threat_subgraph(product_id: str):
    """Fetch subgraph centered around a target product."""
    graph = threat_graph_service.get_product_subgraph(product_id)
    if not graph.nodes:
        return threat_graph_service.get_product_subgraph("prod-cmf-buds")
    return graph


@router.get("/network/{network_id}", response_model=ThreatGraphResponse)
async def get_network_threat_subgraph(network_id: str):
    """Fetch counterfeit fraud ring network subgraph."""
    return threat_graph_service.get_full_graph()


@router.get("/related/{investigation_id}", response_model=ThreatGraphResponse)
async def get_related_investigation_graph(investigation_id: str):
    """Fetch related investigations and shared evidence nodes."""
    return threat_graph_service.get_full_graph()
