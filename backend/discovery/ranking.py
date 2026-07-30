"""
RankingEngine — Sprint 2.2
Ranks ListingGroup objects by investigation priority using:
  1. Price anomaly score     — suspicious underpricing vs. group median
  2. Seller trust score      — unknown / suspicious keywords in seller name
  3. Marketplace risk score  — inherent platform trust tier
  4. Listing completeness    — missing price, thumbnail, availability
  5. Metadata quality        — title noise ratio (replica/oem/wholesale words)

Final priority_score is a weighted composite in [0, 100].
"""
import logging
from typing import List

from backend.discovery.deduplication import (
    _SUSPICIOUS_SELLER_KEYWORDS,
    MARKETPLACE_TRUST_TIER,
)
from backend.schemas.discovery import ListingCandidate, ListingGroup, PriorityScore

logger = logging.getLogger(__name__)

# ── Scoring weights (sum to 1.0) ────────────────────────────────────────────
WEIGHTS = {
    "price_anomaly": 0.30,
    "seller_trust": 0.25,
    "marketplace_risk": 0.20,
    "listing_completeness": 0.15,
    "metadata_quality": 0.10,
}

# Noise / warning words in title that signal suspicious listing
_TITLE_NOISE_WORDS = {
    "replica",
    "master copy",
    "oem",
    "bulk",
    "wholesale",
    "unauthorized",
    "combo",
    "super deal",
    "discounted",
    "shenzhen",
    "trendy",
}

_TRUSTED_SELLER_KEYWORDS = {
    "official",
    "flagship",
    "assured",
    "reliance retail",
    "amazon official",
    "flipkart assured",
    "myntra verified",
    "ajio",
}


def _price_anomaly_score(candidate: ListingCandidate, group_avg: float) -> float:
    """
    Returns 0.0 (no anomaly) → 1.0 (extreme anomaly).
    If price is 0, assume unknown → medium anomaly (0.6).
    If price is >60% below average → high anomaly.
    """
    if candidate.price <= 0 or group_avg <= 0:
        return 0.6
    deviation = (group_avg - candidate.price) / group_avg
    if deviation > 0.60:
        return 1.0
    if deviation > 0.40:
        return 0.8
    if deviation > 0.20:
        return 0.5
    if deviation < 0:
        # Overpriced — slight anomaly
        over = (candidate.price - group_avg) / group_avg
        return min(0.3, over * 0.5)
    return deviation * 1.2  # linear for 0-20% below avg


def _seller_trust_score(seller: str) -> float:
    """
    Returns 0.0 (fully trusted) → 1.0 (highly suspicious).
    """
    seller_lower = seller.lower()
    # Check trusted keywords first
    for kw in _TRUSTED_SELLER_KEYWORDS:
        if kw in seller_lower:
            return 0.05  # Very low risk
    # Check suspicious keywords
    hits = sum(1 for kw in _SUSPICIOUS_SELLER_KEYWORDS if kw in seller_lower)
    if hits >= 3:
        return 0.95
    if hits == 2:
        return 0.75
    if hits == 1:
        return 0.55
    # Unknown seller — moderate risk
    return 0.40


def _marketplace_risk_score(marketplace: str) -> float:
    return MARKETPLACE_TRUST_TIER.get(marketplace.lower(), 0.30)


def _listing_completeness_score(candidate: ListingCandidate) -> float:
    """
    Returns 0.0 (complete) → 1.0 (very incomplete).
    Penalises: missing price, missing thumbnail, missing availability, no seller.
    """
    penalties = 0.0
    if candidate.price <= 0:
        penalties += 0.35
    if not candidate.thumbnail:
        penalties += 0.20
    if candidate.availability.strip().lower() in {"", "unknown", "not available"}:
        penalties += 0.25
    if candidate.seller.lower() in {"unverified seller", "unknown", ""}:
        penalties += 0.20
    return min(1.0, penalties)


def _metadata_quality_score(candidate: ListingCandidate) -> float:
    """
    Returns 0.0 (clean title/metadata) → 1.0 (very noisy).
    Penalises noise words and keyword stuffing in title.
    """
    title_lower = candidate.title.lower()
    hits = sum(1 for w in _TITLE_NOISE_WORDS if w in title_lower)
    # Penalise overly long titles (keyword stuffing)
    word_count = len(title_lower.split())
    stuffing = min(1.0, max(0.0, (word_count - 8) / 12))
    noise_ratio = min(1.0, hits * 0.30 + stuffing * 0.20)
    return noise_ratio


def _investigation_priority_label(score: float) -> str:
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "normal"
    return "low"


class RankingEngine:
    """
    Assigns a composite PriorityScore to each ListingGroup and its individual listings.
    Ranks groups by total_priority_score descending.
    """

    def rank_groups(self, groups: List[ListingGroup]) -> List[ListingGroup]:
        """
        Score and rank all ListingGroups.
        Updates each group's priority_score and investigation_priority in-place.
        Returns groups sorted by total_priority_score (highest first).
        """
        for group in groups:
            group = self._score_group(group)

        ranked = sorted(
            groups,
            key=lambda g: g.priority_score.total_priority_score
            if g.priority_score
            else 0,
            reverse=True,
        )
        logger.info(
            f"RankingEngine: Ranked {len(ranked)} groups. "
            f"Top priority score: {ranked[0].priority_score.total_priority_score:.1f}/100 "
            f"for '{ranked[0].canonical_title}'"
            if ranked
            else "No groups to rank."
        )
        return ranked

    def _score_group(self, group: ListingGroup) -> ListingGroup:
        """
        Score a single ListingGroup using all five ranking signals.
        Picks the most suspicious individual listing to represent the group risk.
        """
        avg_price = group.price_range.get("avg", 0.0)

        candidate_scores = []
        for listing in group.listings:
            pa = _price_anomaly_score(listing, avg_price)
            st = _seller_trust_score(listing.seller)
            mr = _marketplace_risk_score(listing.marketplace)
            lc = _listing_completeness_score(listing)
            mq = _metadata_quality_score(listing)

            composite = (
                pa * WEIGHTS["price_anomaly"]
                + st * WEIGHTS["seller_trust"]
                + mr * WEIGHTS["marketplace_risk"]
                + lc * WEIGHTS["listing_completeness"]
                + mq * WEIGHTS["metadata_quality"]
            ) * 100

            candidate_scores.append((listing, pa, st, mr, lc, mq, composite))

        # Group score = max of individual listing scores (worst-case risk)
        worst = max(candidate_scores, key=lambda x: x[6])
        listing, pa, st, mr, lc, mq, total = worst

        reasoning = self._build_reasoning(listing, pa, st, mr, lc, mq, group)

        group.priority_score = PriorityScore(
            total_priority_score=round(total, 1),
            price_anomaly_score=round(pa, 3),
            seller_trust_score=round(st, 3),
            marketplace_risk_score=round(mr, 3),
            listing_completeness_score=round(lc, 3),
            metadata_quality_score=round(mq, 3),
            reasoning=reasoning,
        )
        group.investigation_priority = _investigation_priority_label(total)
        return group

    @staticmethod
    def _build_reasoning(
        listing: ListingCandidate,
        pa: float,
        st: float,
        mr: float,
        lc: float,
        mq: float,
        group: ListingGroup,
    ) -> List[str]:
        reasons = []

        if pa >= 0.8:
            reasons.append(
                f"Price anomaly: ₹{listing.price:,.0f} is >60% below group average ₹{group.price_range.get('avg', 0):,.0f}"
            )
        elif pa >= 0.5:
            reasons.append(
                f"Price anomaly: ₹{listing.price:,.0f} is >20% below group average"
            )

        if st >= 0.75:
            reasons.append(
                f"High-risk seller: '{listing.seller}' contains suspicious keywords"
            )
        elif st >= 0.40:
            reasons.append(
                f"Unverified seller: '{listing.seller}' cannot be confirmed as authorized"
            )

        if mr >= 0.45:
            reasons.append(
                f"High-risk marketplace: {listing.marketplace} has elevated counterfeit prevalence"
            )

        if lc >= 0.35:
            reasons.append(
                "Incomplete listing: missing price, thumbnail, or availability data"
            )

        if mq >= 0.30:
            reasons.append(
                "Low metadata quality: title contains noise/replica/OEM keywords"
            )

        if len(group.unique_marketplaces) > 2:
            reasons.append(
                f"Cross-platform presence: sold on {len(group.unique_marketplaces)} marketplaces simultaneously"
            )

        if not reasons:
            reasons.append("No major risk signals — low investigation priority")

        return reasons

    def pick_top_targets(
        self,
        groups: List[ListingGroup],
        top_n: int = 5,
    ) -> List[ListingCandidate]:
        """
        From ranked groups, pick the single best investigation target listing per group.
        Selects the listing with the highest individual risk within each group,
        returns top_n overall candidates.
        """
        targets = []
        for group in groups:
            if not group.listings:
                continue
            # Pick the listing with the highest risk score from the group
            avg_price = group.price_range.get("avg", 0.0)
            best = max(
                group.listings,
                key=lambda c: (
                    _seller_trust_score(c.seller) * 0.4
                    + _price_anomaly_score(c, avg_price) * 0.4
                    + _marketplace_risk_score(c.marketplace) * 0.2
                ),
            )
            targets.append(best)
        return targets[:top_n]
