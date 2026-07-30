"""
memory.py — Organizational Memory Schema DTOs
Pydantic models representing historical investigation search results, precedent matches, and similarity scores.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryMatchItem(BaseModel):
    id: str = Field(..., description="Entity or Investigation ID")
    title: str = Field(..., description="Discovered title or name")
    category: str = Field(
        ..., description="Entity category (Investigation, Seller, Product, Evidence)"
    )
    similarity_pct: float = Field(
        ..., description="Vector similarity match percentage (0-100)"
    )
    verdict: str = Field(
        ..., description="Historical verdict (CRITICAL, HIGH, MEDIUM, LOW)"
    )
    marketplace: Optional[str] = Field(default=None, description="Marketplace platform")
    seller: Optional[str] = Field(default=None, description="Associated seller")
    summary: str = Field(..., description="Historical precedent summary")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MemorySearchResponse(BaseModel):
    query: str
    total_matches: int
    matches: List[MemoryMatchItem]
    recommendation: str = Field(
        ..., description="AI historical precedent recommendation"
    )
    meta: Dict[str, Any] = Field(default_factory=dict)
