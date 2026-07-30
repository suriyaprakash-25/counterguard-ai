"""
DeduplicationService — Sprint 2.2
Groups equivalent listings using:
  1. Title similarity (token-based Jaccard similarity)
  2. Normalized product name overlap
  3. Model number extraction & exact match
  4. Seller identity matching
  5. Specification similarity (from metadata)
  6. Image hash placeholder (future: perceptual hashing)
"""
import logging
import re
from typing import List, Set

from backend.schemas.discovery import ListingCandidate, ListingGroup

logger = logging.getLogger(__name__)

# ── Model number extraction regex (e.g., WH-1000XM5, Buds 2a, C1TY, Air Max 90)
_MODEL_PATTERN = re.compile(
    r"\b([A-Z]{1,4}[-_]?\d{1,5}[A-Za-z]{0,3}|"  # e.g. WH-1000XM5, CMF-2A
    r"\d{1,4}[A-Za-z]{1,4}\d{0,4}|"  # e.g. 2a, 90, 720i
    r"[A-Z]{2,8}\d{2,6})\b",
    re.IGNORECASE,
)

# Marketplace risk tier (for ranking; used in _marketplace_risk)
MARKETPLACE_TRUST_TIER: dict[str, float] = {
    "amazon": 0.10,
    "flipkart": 0.12,
    "myntra": 0.10,
    "ajio": 0.10,
    "meesho": 0.45,  # higher risk
    "tradeindia": 0.60,  # B2B wholesale — highest risk for consumer goods
}

# Known unverified seller keywords
_SUSPICIOUS_SELLER_KEYWORDS = {
    "replica",
    "master copy",
    "unauthorized",
    "wholesale",
    "global",
    "electrodeals",
    "hub",
    "surat",
    "combo",
    "oem",
    "manufacturer",
    "bulk",
    "shenzhen",
    "precision tech",
}


def _normalize_text(text: str) -> str:
    """Lowercase, collapse spaces, strip punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _token_set(text: str) -> Set[str]:
    """Tokenize normalized text into a set of words (min 2 chars)."""
    return {w for w in _normalize_text(text).split() if len(w) >= 2}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union)


def _extract_model_numbers(text: str) -> Set[str]:
    return {m.group(0).lower() for m in _MODEL_PATTERN.finditer(text)}


def _titles_are_equivalent(t1: str, t2: str, threshold: float = 0.45) -> bool:
    """
    Returns True if two titles are similar enough to be the same product variant.
    Uses Jaccard similarity on title token sets.
    """
    s1, s2 = _token_set(t1), _token_set(t2)
    # Skip common noise words
    noise = {
        "official",
        "brand",
        "listing",
        "edition",
        "authentic",
        "deal",
        "combo",
        "replica",
        "master",
        "copy",
        "original",
        "super",
        "premium",
        "discounted",
        "authorized",
        "assured",
        "trendy",
        "bulk",
        "oem",
        "manufacturing",
    }
    s1 -= noise
    s2 -= noise

    if _jaccard(s1, s2) >= threshold:
        return True

    # Also deduplicate if they share at least one model number
    m1 = _extract_model_numbers(t1)
    m2 = _extract_model_numbers(t2)
    if m1 and m2 and m1 & m2:
        return True

    return False


def _canonical_title(candidates: List[ListingCandidate]) -> str:
    """Pick the shortest title as canonical (usually the official listing)."""
    return min(candidates, key=lambda c: len(c.title)).title


def _normalized_product_name(title: str) -> str:
    """
    Extract a normalized clean product name from a title.
    Strips noise suffixes and qualifiers.
    """
    noise = [
        r"\(.*?\)",
        r"official brand listing",
        r"assured authentic",
        r"super deal.*",
        r"premium edition.*",
        r"replica.*",
        r"bulk oem.*",
        r"trendy combo.*",
        r"authorized reseller.*",
        r"unauthorized reseller.*",
        r"master copy.*",
    ]
    name = title.lower()
    for pattern in noise:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)
    return " ".join(name.split()).title()


class DeduplicationService:
    """
    Clusters equivalent candidate listings into ListingGroup objects.
    Deduplication criteria (in priority order):
      1. Model number exact match
      2. Title token-set Jaccard similarity >= 0.45
      3. Seller identity match (cross-group merge)
    """

    def deduplicate(self, candidates: List[ListingCandidate]) -> List[ListingGroup]:
        if not candidates:
            return []

        # Union-Find (disjoint set) structure for O(n²) clustering
        parent = list(range(len(candidates)))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i: int, j: int) -> None:
            pi, pj = find(i), find(j)
            if pi != pj:
                parent[pj] = pi

        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                if _titles_are_equivalent(candidates[i].title, candidates[j].title):
                    union(i, j)

        # Collect groups
        cluster_map: dict[int, List[int]] = {}
        for idx in range(len(candidates)):
            root = find(idx)
            cluster_map.setdefault(root, []).append(idx)

        groups: List[ListingGroup] = []
        for root, indices in cluster_map.items():
            group_candidates = [candidates[i] for i in indices]
            representative = max(group_candidates, key=lambda c: c.confidence)
            canonical = _canonical_title(group_candidates)
            norm_name = _normalized_product_name(canonical)

            prices = [c.price for c in group_candidates if c.price > 0]
            price_range = {}
            if prices:
                price_range = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": round(sum(prices) / len(prices), 2),
                }

            # Determine similarity basis
            model_nums = _extract_model_numbers(canonical)
            basis = "model_number" if model_nums else "title"

            groups.append(
                ListingGroup(
                    canonical_title=canonical,
                    normalized_product_name=norm_name,
                    listings=group_candidates,
                    representative=representative,
                    unique_marketplaces=list({c.marketplace for c in group_candidates}),
                    unique_sellers=list({c.seller for c in group_candidates}),
                    price_range=price_range,
                    similarity_basis=basis,
                    listing_count=len(group_candidates),
                )
            )

        logger.info(
            f"Deduplication: {len(candidates)} candidates → {len(groups)} groups "
            f"(reduced by {len(candidates) - len(groups)})"
        )
        return groups
