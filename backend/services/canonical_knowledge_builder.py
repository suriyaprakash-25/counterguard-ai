import logging
import re
from typing import Any, Dict, List, Optional

from backend.schemas.canonical_product import CanonicalProductKnowledge
from backend.schemas.official_product import OfficialProductProfile

logger = logging.getLogger(__name__)


class CanonicalKnowledgeBuilder:
    """
    CanonicalKnowledgeBuilder (Sprint 17 Foundation Component)

    Transforms extracted OfficialProductProfile baselines and auxiliary multi-source catalogs
    (FCC DB, BIS DB, GSMArena, retail catalogs) into a single, source-agnostic `CanonicalProductKnowledge`
    object consumed by all specialist AI agents.
    """

    def build_slug(self, brand: str, product_name: str) -> str:
        """Generates a unique canonical ID slug."""
        combined = f"{brand} {product_name}".lower().strip()
        slug = re.sub(r"[^\w\s-]", "", combined)
        return re.sub(r"[-\s]+", "-", slug)

    def build_from_profile(
        self,
        profile: OfficialProductProfile,
        auxiliary_sources: Optional[List[Dict[str, Any]]] = None,
    ) -> CanonicalProductKnowledge:
        """
        Builds a CanonicalProductKnowledge object from an OfficialProductProfile.
        Fuses auxiliary knowledge sources if present.
        """
        logger.debug(
            f"[CanonicalKnowledgeBuilder] Compiling canonical knowledge for '{profile.normalized_name}'."
        )

        canonical_id = self.build_slug(profile.brand, profile.product_name)
        provenance = [profile.source or "official_website"]

        if auxiliary_sources:
            for aux in auxiliary_sources:
                src_name = aux.get("source_name", "external_db")
                if src_name not in provenance:
                    provenance.append(src_name)

        return CanonicalProductKnowledge(
            brand=profile.brand,
            product_name=profile.product_name,
            canonical_id=canonical_id,
            category=profile.category or "General",
            model_number=profile.model_number,
            manufacturer=profile.manufacturer or profile.brand,
            official_url=profile.official_url,
            msrp=profile.msrp,
            currency=profile.currency or "INR",
            verified_images=profile.official_images,
            canonical_specs=profile.specifications,
            variants=profile.colors,
            certifications=profile.metadata.get(
                "certifications", ["CE", "BIS", "RoHS"]
            ),
            warranty_terms=profile.warranty,
            overall_confidence=profile.confidence,
            provenance_sources=provenance,
            evidence_trail=profile.evidence_trail,
            metadata=profile.metadata,
        )
