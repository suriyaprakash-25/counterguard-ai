import logging
import urllib.parse
from typing import List, Set

from backend.schemas.discovery_engine import SourceCandidate

logger = logging.getLogger(__name__)


class SourceDeduplicationEngine:
    """
    SourceDeduplicationEngine (Sprint 17 Phase 2 Improvement 1)

    Dedicated pipeline stage responsible for candidate URL normalization and deduplication.
    Ensures candidates like 'https://apple.com/airpods' and 'https://www.apple.com/airpods/'
    are merged into a single candidate BEFORE the ranking and verification stages.
    """

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalizes a candidate URL into a canonical comparison string.
        Strips scheme trailing slashes, www. prefixes, and query parameters if needed.
        """
        if not url:
            return ""
        try:
            parsed = urllib.parse.urlparse(url.strip().lower())
            netloc = parsed.netloc.replace("www.", "")
            path = parsed.path.rstrip("/")
            # Return canonical scheme + host + path
            return f"{parsed.scheme}://{netloc}{path}"
        except Exception:
            return url.strip().lower()

    def deduplicate(self, candidates: List[SourceCandidate]) -> List[SourceCandidate]:
        """
        Deduplicates candidate list by canonical URL.
        Preserves candidate with highest confidence / provider priority when duplicates occur.
        """
        if not candidates:
            return []

        seen_urls: Set[str] = set()
        deduped: List[SourceCandidate] = []

        # Sort candidate pool temporarily so higher confidence / official store entries come first
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (
                c.confidence,
                100 if c.source_type == "Official Store" else 10,
            ),
            reverse=True,
        )

        for candidate in sorted_candidates:
            clean_url = self.normalize_url(candidate.url)
            if clean_url not in seen_urls:
                seen_urls.add(clean_url)
                deduped.append(candidate)
            else:
                logger.debug(
                    f"[SourceDeduplicationEngine] Merged duplicate candidate URL: '{candidate.url}'"
                )

        return deduped
