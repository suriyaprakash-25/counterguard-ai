import logging
import urllib.parse
from typing import Dict, List, Set

from backend.schemas.discovery_engine import SourceCandidate

logger = logging.getLogger(__name__)


class SourceRankingEngine:
    """
    SourceRankingEngine (Sprint 17 Phase 2 Deliverable)

    Ranks, scores, sorts, and deduplicates discovery candidates based on configurable rules:
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

    def remove_duplicates(
        self, candidates: List[SourceCandidate]
    ) -> List[SourceCandidate]:
        """
        Deduplicates candidate list based on canonical normalized URL strings.
        Preserves highest-scoring entry when duplicates exist.
        """
        seen_urls: Set[str] = set()
        unique_candidates: List[SourceCandidate] = []

        # Sort first so highest scoring candidate of a duplicate URL wins
        sorted_candidates = self.sort(candidates)

        for cand in sorted_candidates:
            clean_url = self.normalize_url(cand.url)
            if clean_url not in seen_urls:
                seen_urls.add(clean_url)
                unique_candidates.append(cand)

        return unique_candidates

    def sort(self, candidates: List[SourceCandidate]) -> List[SourceCandidate]:
        """
        Sorts candidates in descending order of priority score.
        """
        return sorted(candidates, key=lambda c: self.score(c), reverse=True)

    def rank(self, candidates: List[SourceCandidate]) -> List[SourceCandidate]:
        """
        Primary entry point: Removes duplicates and sorts candidate sources by priority rank.
        """
        if not candidates:
            return []
        deduped = self.remove_duplicates(candidates)
        return self.sort(deduped)

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalizes a URL string for deduplication comparison.
        """
        if not url:
            return ""
        try:
            parsed = urllib.parse.urlparse(url.strip().lower())
            # Strip trailing slash and www. prefix
            netloc = parsed.netloc.replace("www.", "")
            path = parsed.path.rstrip("/")
            return f"{parsed.scheme}://{netloc}{path}"
        except Exception:
            return url.strip().lower()
