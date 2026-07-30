import logging
from typing import Dict, List

from backend.schemas.discovery_engine import SourceCandidate
from backend.services.source_deduplication_engine import SourceDeduplicationEngine

logger = logging.getLogger(__name__)


class SourceRankingEngine:
    """
    SourceRankingEngine (Sprint 17 Phase 2 Deliverable)

    Scores and ranks candidate sources based on configurable rules:
      1. Official Store / Official Domain  (Weight: 100)
      2. Brand Store                      (Weight: 80)
      3. Authorized Retailer              (Weight: 60)
      4. Trusted Marketplace              (Weight: 40)
      5. Other / Unverified               (Weight: 20)
    """

    TYPE_WEIGHTS: Dict[str, float] = {
        "official store": 100.0,
        "official brand flagship": 100.0,
        "brand store": 80.0,
        "authorized retailer": 60.0,
        "trusted marketplace": 40.0,
        "marketplace": 30.0,
        "other": 20.0,
    }

    def __init__(self):
        self.deduplication_engine = SourceDeduplicationEngine()

    def score(self, candidate: SourceCandidate) -> float:
        """
        Calculates numerical priority score for a candidate source.
        Combines type weight and provider confidence.
        """
        stype = candidate.source_type.strip().lower()
        base_weight = self.TYPE_WEIGHTS.get(stype, 20.0)
        confidence_multiplier = (
            candidate.confidence if candidate.confidence > 0 else 0.5
        )
        total_score = base_weight * confidence_multiplier
        return round(total_score, 2)

    def sort(self, candidates: List[SourceCandidate]) -> List[SourceCandidate]:
        """
        Sorts candidates in descending order of priority score.
        """
        return sorted(candidates, key=lambda c: self.score(c), reverse=True)

    def rank(self, candidates: List[SourceCandidate]) -> List[SourceCandidate]:
        """
        Primary entry point: Ranks pre-deduplicated candidate sources by priority score.
        """
        if not candidates:
            return []
        return self.sort(candidates)

    def remove_duplicates(
        self, candidates: List[SourceCandidate]
    ) -> List[SourceCandidate]:
        """Convenience delegate method for backward compatibility."""
        return self.deduplication_engine.deduplicate(candidates)
