"""
memory.py — Phase 3: Organizational Memory REST API Routes
FastAPI endpoints for querying vector organizational memory precedents for investigations, sellers, products, and evidence.
"""
from fastapi import APIRouter, Query

from backend.agents.historical_memory_agent import historical_memory_agent
from backend.schemas.memory import MemorySearchResponse

router = APIRouter(prefix="/memory", tags=["Organizational Memory"])


@router.get("/similar-investigations", response_model=MemorySearchResponse)
async def search_similar_investigations(
    query: str = Query(..., description="Target search query or title")
):
    """Search vector organizational memory for similar historical investigations."""
    return historical_memory_agent.search_similar_investigations(query)


@router.get("/similar-sellers", response_model=MemorySearchResponse)
async def search_similar_sellers(
    seller: str = Query(..., description="Seller business name")
):
    """Search vector organizational memory for historical seller precedents."""
    return historical_memory_agent.search_similar_sellers(seller)


@router.get("/similar-products", response_model=MemorySearchResponse)
async def search_similar_products(
    product: str = Query(..., description="Product model name")
):
    """Search vector organizational memory for historical product precedents."""
    return historical_memory_agent.search_similar_products(product)


@router.get("/similar-evidence", response_model=MemorySearchResponse)
async def search_similar_evidence(
    query: str = Query(..., description="Evidence keyword")
):
    """Search vector organizational memory for matching evidence precedents."""
    return historical_memory_agent.search_similar_evidence(query)
