from collections import defaultdict
from typing import Any, Dict, List

from backend.graphrag.models.domain import PatternMatch


class PatternDetectionService:
    """
    Detects repeated patterns across historical investigations (sellers, invoices, hashes).
    """

    def detect_patterns(  # noqa: C901
        self, ranked_episodes: List[Dict[str, Any]]
    ) -> List[PatternMatch]:
        patterns = []

        seller_counts = defaultdict(list)
        invoice_counts = defaultdict(list)
        hash_counts = defaultdict(list)
        phone_counts = defaultdict(list)

        for ep_data in ranked_episodes:
            ep = ep_data["episode"]
            seller_counts[ep.seller_identity.name].append(ep.id)

            if ep.seller_identity.phone:
                phone_counts[ep.seller_identity.phone].append(ep.id)

            for ev in ep.evidence_list:
                if ev.evidence_type.value == "Invoice":
                    # Simple matching on exact invoice text/metadata for now
                    invoice_counts[ev.content].append(ep.id)
                elif ev.evidence_type.value == "Image":
                    # Assume metadata contains hash
                    img_hash = ev.metadata.get("image_hash")
                    if img_hash:
                        hash_counts[img_hash].append(ep.id)

        # Build PatternMatch objects
        for seller, ids in seller_counts.items():
            if len(ids) > 1:
                patterns.append(
                    PatternMatch(
                        pattern_type="repeated_seller",
                        description=f"Seller '{seller}' appears in multiple investigations.",
                        frequency=len(ids),
                        associated_investigation_ids=ids,
                    )
                )

        for phone, ids in phone_counts.items():
            if len(ids) > 1:
                patterns.append(
                    PatternMatch(
                        pattern_type="repeated_phone",
                        description=f"Phone number '{phone}' appears in multiple investigations.",
                        frequency=len(ids),
                        associated_investigation_ids=ids,
                    )
                )

        for inv, ids in invoice_counts.items():
            if len(ids) > 1:
                patterns.append(
                    PatternMatch(
                        pattern_type="repeated_invoice",
                        description="The exact same invoice content was found in multiple investigations.",
                        frequency=len(ids),
                        associated_investigation_ids=ids,
                    )
                )

        for h, ids in hash_counts.items():
            if len(ids) > 1:
                patterns.append(
                    PatternMatch(
                        pattern_type="repeated_image_hash",
                        description="The same image hash was detected across multiple listings.",
                        frequency=len(ids),
                        associated_investigation_ids=ids,
                    )
                )

        patterns.sort(key=lambda x: x.frequency, reverse=True)
        return patterns
