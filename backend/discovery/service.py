import logging
import re
import time
from datetime import datetime

from backend.discovery.deduplication import DeduplicationService
from backend.discovery.marketplace_health import MarketplaceHealthService
from backend.discovery.memory import DiscoveryMemoryService
from backend.discovery.ranking import RankingEngine
from backend.discovery.router import MarketplaceRouter
from backend.schemas.discovery import DiscoverySearchRequest, DiscoverySearchResponse

logger = logging.getLogger(__name__)


class DiscoveryService:
    """
    Core Product Discovery Service with Memory Cache & Provenance.
    Normalizes query strings, checks Discovery Memory, delegates to MarketplaceRouter,
    deduplicates into ListingGroups, enriches confidence & provenance, and ranks targets.
    """

    def __init__(self, router: MarketplaceRouter = None):
        self.router = router or MarketplaceRouter()
        self.deduplicator = DeduplicationService()
        self.ranker = RankingEngine()

    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normalizes product search query string.
        """
        if not query:
            return ""
        normalized = re.sub(r"\s+", " ", query.strip())
        return normalized

    async def discover_products(
        self, request: DiscoverySearchRequest
    ) -> DiscoverySearchResponse:
        start_time = time.time()
        normalized_q = self.normalize_query(request.query)

        logger.info(
            f"DiscoveryService initiating product search for: '{request.query}' (normalized: '{normalized_q}')"
        )

        # ── Refinement 1: Discovery Memory Check ──────────────────────────────
        if request.use_memory_cache:
            cached_resp = DiscoveryMemoryService.get(normalized_q)
            if cached_resp:
                logger.info(
                    f"[DiscoveryService] Returning cached discovery memory for query '{normalized_q}'"
                )
                return cached_resp

        # ── Stage 1: Collect raw candidates from marketplace adapters ──────────
        candidates = await self.router.search(
            query=normalized_q,
            target_marketplaces=request.marketplaces,
            limit_per_marketplace=request.limit_per_marketplace,
        )

        # ── Refinement 3 & 4: Multi-stage Confidence & Provenance Enrichment ───
        for c in candidates:
            # Query match quality
            c.search_confidence = (
                0.92 if normalized_q.lower() in c.title.lower() else 0.85
            )
            c.discovered_via = "Marketplace API"
            if not c.provenance_chain:
                c.provenance_chain = [f"Marketplace API: {c.marketplace}"]
            else:
                c.provenance_chain.append(f"Marketplace API: {c.marketplace}")

        # ── Stage 2: Deduplication ────────────────────────────────────────────
        groups = self.deduplicator.deduplicate(candidates)

        # Update matching confidence after deduplication
        for grp in groups:
            match_conf = 0.95 if len(grp.listings) > 1 else 0.85
            for candidate in grp.listings:
                candidate.matching_confidence = match_conf
                candidate.discovery_confidence = round(
                    (candidate.search_confidence + candidate.matching_confidence) / 2, 2
                )
                if (
                    "Deduplication: Union-Find Canonical Clustering"
                    not in candidate.provenance_chain
                ):
                    candidate.provenance_chain.append(
                        "Deduplication: Union-Find Canonical Clustering"
                    )

        # ── Stage 3: Ranking ──────────────────────────────────────────────────
        ranked_groups = self.ranker.rank_groups(groups)

        # ── Stage 4: Top investigation targets ───────────────────────────────
        top_targets = self.ranker.pick_top_targets(ranked_groups, top_n=5)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        marketplaces_searched = (
            request.marketplaces or self.router.get_supported_marketplaces()
        )

        # ── Refinement 2: Marketplace Health Scores Matrix ─────────────────────
        health_matrix = {
            mp: MarketplaceHealthService.get_health(mp).model_dump()
            for mp in marketplaces_searched
        }

        response = DiscoverySearchResponse(
            query=request.query,
            normalized_query=normalized_q,
            marketplaces_searched=marketplaces_searched,
            candidates=candidates,
            listing_groups=ranked_groups,
            top_investigation_targets=top_targets,
            metadata={
                "candidate_count": len(candidates),
                "group_count": len(ranked_groups),
                "top_target_count": len(top_targets),
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "search_engine_version": "CounterGuard-Discovery-v2.2",
                "deduplication_reduction": len(candidates) - len(ranked_groups),
                "marketplace_health_scores": health_matrix,
                "from_memory": False,
            },
        )

        # Store in Discovery Memory for fast re-querying
        DiscoveryMemoryService.put(normalized_q, response)

        return response
