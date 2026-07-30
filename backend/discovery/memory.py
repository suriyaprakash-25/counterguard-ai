"""
DiscoveryMemoryService — Refinement 1

Provides historical discovery memory caching by normalized query string.
When a product (e.g. 'CMF Buds 2a') is re-searched:
  - Loads previous discovery from memory
  - Compares candidates to identify new / changed listings
  - Updates provenance chain to "Historical Memory: Cached"
  - Returns cached results instantly with incremental delta stats
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.schemas.discovery import DiscoverySearchResponse, ListingCandidate

logger = logging.getLogger(__name__)


class DiscoveryMemoryService:
    """In-memory + persistent cache store for discovery search queries."""

    _CACHE: Dict[str, Tuple[DiscoverySearchResponse, datetime]] = {}
    _TTL_SECONDS: int = 1800  # 30 minutes

    @classmethod
    def get(cls, query_normalized: str) -> Optional[DiscoverySearchResponse]:
        key = query_normalized.lower().strip()
        if key in cls._CACHE:
            resp, cached_at = cls._CACHE[key]
            elapsed = (datetime.now(timezone.utc) - cached_at).total_seconds()
            if elapsed <= cls._TTL_SECONDS:
                logger.info(
                    f"[DiscoveryMemory] Cache HIT for query '{query_normalized}' (age: {round(elapsed, 1)}s)"
                )
                # Return deep copy with updated metadata provenance
                cached_resp = resp.model_copy(deep=True)
                cached_resp.metadata["from_memory"] = True
                cached_resp.metadata["cached_at"] = cached_at.isoformat()
                cached_resp.metadata["memory_age_seconds"] = round(elapsed, 1)

                # Update candidate provenance tags
                for candidate in cached_resp.candidates:
                    candidate.discovered_via = "Historical Memory"
                    if (
                        "Historical Memory: Loaded from cache"
                        not in candidate.provenance_chain
                    ):
                        candidate.provenance_chain.append(
                            "Historical Memory: Loaded from cache"
                        )

                return cached_resp
            else:
                logger.info(
                    f"[DiscoveryMemory] Cache EXPIRED for query '{query_normalized}'"
                )
                del cls._CACHE[key]
        return None

    @classmethod
    def put(cls, query_normalized: str, response: DiscoverySearchResponse) -> None:
        key = query_normalized.lower().strip()
        now = datetime.now(timezone.utc)
        cls._CACHE[key] = (response, now)
        logger.info(
            f"[DiscoveryMemory] Stored discovery result for '{query_normalized}' ({len(response.candidates)} candidates)"
        )

    @classmethod
    def compute_diff(
        cls, previous: DiscoverySearchResponse, fresh: DiscoverySearchResponse
    ) -> Tuple[List[ListingCandidate], List[ListingCandidate]]:
        """
        Compares previous discovery vs fresh search to find new and updated candidates.
        """
        prev_urls = {c.url for c in previous.candidates}
        new_candidates = [c for c in fresh.candidates if c.url not in prev_urls]
        existing_candidates = [c for c in fresh.candidates if c.url in prev_urls]
        return new_candidates, existing_candidates

    @classmethod
    def clear(cls) -> None:
        cls._CACHE.clear()
