import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ListingCandidate(BaseModel):
    """
    Represents a discovered product candidate listing from a marketplace search adapter.
    Includes stage-specific confidence scores and full discovery provenance lineage.
    """

    id: str = Field(default_factory=lambda: f"cand-{uuid.uuid4().hex[:8]}")
    marketplace: str = "Global"
    title: str
    url: str
    price: float = 0.0
    seller: str = "Unverified Seller"
    thumbnail: Optional[str] = None
    currency: str = "INR"
    availability: str = "In Stock"
    discovery_source: str = "Marketplace Search Adapter"
    confidence: float = Field(0.85, ge=0.0, le=1.0)

    # ── Refinement 3: Multi-Stage Discovery Confidence ────────────────────────
    search_confidence: float = Field(
        0.90, ge=0.0, le=1.0, description="Query match quality score"
    )
    matching_confidence: float = Field(
        0.85, ge=0.0, le=1.0, description="Deduplication & entity match quality"
    )
    discovery_confidence: float = Field(
        0.88, ge=0.0, le=1.0, description="Overall discovery confidence"
    )
    investigation_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Verdict confidence when investigated"
    )

    # ── Refinement 4: Discovery Provenance Lineage ────────────────────────────
    discovered_via: str = Field(
        "Search",
        description="Marketplace API | Search | Scraper | Manual | Historical Memory",
    )
    provenance_chain: List[str] = Field(
        default_factory=lambda: ["Marketplace API: Search Adapter"],
        description="Lineage trace steps explaining discovery origin",
    )

    metadata: Dict[str, Any] = Field(default_factory=dict)

    # ── Feature 4: Full Candidate Lineage Metadata ─────────────────────────────
    candidate_id: Optional[str] = None
    http_request_id: Optional[str] = None
    response_sha256: Optional[str] = None
    evidence_archive_id: Optional[str] = None
    parser_version: str = Field("v1.2.0-bs4", description="Parser engine version")
    parser_confidence: float = Field(
        95.0, description="Parser extraction confidence score (0-100)"
    )
    retrieval_mode: str = Field(
        "LIVE_HTTP",
        description="LIVE_HTTP | OFFICIAL_API | CACHE | HISTORICAL_MEMORY | FALLBACK",
    )
    deduplication_group_id: Optional[str] = None
    ranking_score: float = 0.0
    investigation_id: Optional[str] = None
    report_id: Optional[str] = None


class DiscoverySearchRequest(BaseModel):
    query: str
    marketplaces: Optional[List[str]] = None
    limit_per_marketplace: int = Field(5, ge=1, le=20)
    use_memory_cache: bool = Field(
        True, description="Load previous discovery memory if available"
    )


# ── Refinement 2: Marketplace Health Score Schema ────────────────────────────


class MarketplaceHealthInfo(BaseModel):
    marketplace: str
    health_score: int = Field(
        ..., ge=0, le=100, description="Live reliability / health score 0-100"
    )
    status: str = "Operational"  # "Operational" | "Degraded" | "Offline"
    latency_ms: float = 120.0
    captcha_rate: float = 0.0
    data_quality_score: int = 95


# ── Sprint 2.2: Deduplication & Ranking Models ────────────────────────────────


class PriorityScore(BaseModel):
    """
    Composite priority score explaining why a listing group is ranked high for investigation.
    All component scores are in [0, 1] range; total_priority_score is in [0, 100].
    """

    total_priority_score: float = Field(0.0, ge=0.0, le=100.0)
    # Component sub-scores
    price_anomaly_score: float = Field(0.0, ge=0.0, le=1.0)
    seller_trust_score: float = Field(0.0, ge=0.0, le=1.0)  # higher = less trusted
    marketplace_risk_score: float = Field(0.0, ge=0.0, le=1.0)
    listing_completeness_score: float = Field(
        0.0, ge=0.0, le=1.0
    )  # higher = more incomplete
    metadata_quality_score: float = Field(0.0, ge=0.0, le=1.0)  # higher = lower quality
    # Human-readable breakdown
    reasoning: List[str] = Field(default_factory=list)


class ListingGroup(BaseModel):
    """
    A cluster of deduplicated equivalent listings for the same underlying product variant.
    Produced by the DeduplicationService and enriched by the RankingEngine.
    """

    group_id: str = Field(default_factory=lambda: f"grp-{uuid.uuid4().hex[:8]}")
    canonical_title: str
    normalized_product_name: str
    # All deduplicated candidates in this group (across marketplaces)
    listings: List[ListingCandidate]
    # Best representative listing for the group (highest confidence)
    representative: Optional[ListingCandidate] = None
    # Cross-listing deduplication metadata
    unique_marketplaces: List[str] = Field(default_factory=list)
    unique_sellers: List[str] = Field(default_factory=list)
    price_range: Dict[str, float] = Field(
        default_factory=dict
    )  # {"min": x, "max": y, "avg": z}
    similarity_basis: str = (
        "title"  # "title" | "model_number" | "seller" | "specification"
    )
    listing_count: int = 0
    # Ranking output
    priority_score: Optional[PriorityScore] = None
    investigation_priority: str = "normal"  # "critical" | "high" | "normal" | "low"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DiscoverySearchResponse(BaseModel):
    query: str
    normalized_query: str
    marketplaces_searched: List[str]
    # Raw flat candidate list (Sprint 2.1 — preserved for backward compat)
    candidates: List[ListingCandidate]
    # Sprint 2.2: Deduplicated groups ranked by investigation priority
    listing_groups: List[ListingGroup] = Field(default_factory=list)
    # Top N candidates ranked for immediate investigation
    top_investigation_targets: List[ListingCandidate] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
