import logging
import time
from typing import List, Optional

from backend.providers.discovery.base_provider import SearchProvider
from backend.providers.discovery.static_brand_provider import StaticBrandProvider
from backend.schemas.discovery_engine import DiscoveryResult, SourceCandidate
from backend.services.source_ranking_engine import SourceRankingEngine
from backend.services.source_verification_engine import SourceVerificationEngine

logger = logging.getLogger(__name__)


class DiscoveryPipeline:
    """
    DiscoveryPipeline (Sprint 17 Phase 2 Deliverable)

    Orchestrates provider execution, candidate aggregation, source ranking, and deterministic verification.
    Extensible architecture supporting registering multiple SearchProvider implementations.
    """

    def __init__(self, providers: Optional[List[SearchProvider]] = None):
        self.providers: List[SearchProvider] = providers or [StaticBrandProvider()]
        self.ranking_engine = SourceRankingEngine()
        self.verification_engine = SourceVerificationEngine()
        logger.info(
            f"[DiscoveryPipeline] Initialized with {len(self.providers)} providers."
        )

    def register_provider(self, provider: SearchProvider) -> None:
        """Registers a new SearchProvider instance into the discovery pipeline."""
        self.providers.append(provider)
        logger.info(
            f"[DiscoveryPipeline] Registered provider '{provider.provider_name}'."
        )

    def normalize_request(self, query: str, brand: str = "") -> str:
        """Normalizes raw search query and brand inputs."""
        combined = f"{brand} {query}".strip().lower()
        return " ".join(combined.split())

    def select_providers(self, brand: str, query: str) -> List[SearchProvider]:
        """Selects active providers that support discovery for the given query and brand."""
        active = [
            p
            for p in self.providers
            if p.supports(brand=brand) or p.supports(brand="", domain=query)
        ]
        return active if active else self.providers

    def run(self, query: str, brand: str = "") -> DiscoveryResult:
        """
        Primary execution entry point for the DiscoveryPipeline:
          1. Normalize Request
          2. Select Providers
          3. Execute Providers
          4. Collect Candidates
          5. Rank Results (SourceRankingEngine)
          6. Verify Results (SourceVerificationEngine)
          7. Return DiscoveryResult
        """
        start_time = time.time()
        normalized = self.normalize_request(query=query, brand=brand)
        active_providers = self.select_providers(brand=brand, query=query)
        providers_used = [p.provider_name for p in active_providers]

        raw_candidates: List[SourceCandidate] = []
        for provider in active_providers:
            try:
                if provider.health_check():
                    candidates = provider.search(query=query, brand=brand)
                    raw_candidates.extend(candidates)
            except Exception as err:
                logger.error(
                    f"[DiscoveryPipeline] Error executing provider '{provider.provider_name}': {err}"
                )

        # Rank candidates
        ranked_candidates = self.ranking_engine.rank(raw_candidates)

        # Verify top candidates
        verified_source: Optional[SourceCandidate] = None
        verification_reasoning = "No candidate sources discovered."
        pipeline_status = "no_candidates_found"
        pipeline_confidence = 0.0

        for cand in ranked_candidates:
            is_verified, reason = self.verification_engine.verify_source(
                cand, brand=brand
            )
            if is_verified:
                verified_source = cand
                verification_reasoning = reason
                pipeline_status = "success"
                pipeline_confidence = cand.confidence
                break
            else:
                logger.debug(
                    f"[DiscoveryPipeline] Verification rejected candidate '{cand.url}': {reason}"
                )
                if pipeline_status == "no_candidates_found":
                    pipeline_status = "verification_failed"
                    verification_reasoning = reason

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

        return DiscoveryResult(
            query=query,
            brand=brand,
            normalized_name=normalized,
            providers_used=providers_used,
            candidate_sources=ranked_candidates,
            verified_source=verified_source,
            confidence=pipeline_confidence,
            reasoning=verification_reasoning,
            status=pipeline_status,
            discovery_time_ms=elapsed_ms,
            metadata={
                "raw_candidate_count": len(raw_candidates),
                "ranked_candidate_count": len(ranked_candidates),
            },
        )
