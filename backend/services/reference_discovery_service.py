import logging
from typing import Any, Dict, Optional, Tuple

from backend.schemas.discovery_engine import DiscoveryResult
from backend.schemas.official_product import OfficialProductProfile
from backend.services.discovery_pipeline import DiscoveryPipeline

logger = logging.getLogger(__name__)


class ReferenceDiscoveryService:
    """
    ReferenceDiscoveryService (Sprint 17 Phase 2 Deliverable)

    Orchestrates product reference discovery by invoking the `DiscoveryPipeline`, ranking candidates,
    executing deterministic verification, and building the `OfficialProductProfile` baseline.
    """

    def __init__(self, pipeline: Optional[DiscoveryPipeline] = None):
        self.pipeline = pipeline or DiscoveryPipeline()
        logger.info("Initializing ReferenceDiscoveryService with DiscoveryPipeline.")

    def discover(
        self, product_name: str, brand: str = ""
    ) -> Tuple[DiscoveryResult, OfficialProductProfile]:
        """
        Discovers and retrieves reference sources via DiscoveryPipeline, then returns
        a Tuple[DiscoveryResult, OfficialProductProfile].
        """
        logger.debug(
            f"[ReferenceDiscoveryService] Discover executing pipeline for product='{product_name}', brand='{brand}'."
        )

        discovery_result = self.pipeline.run(query=product_name, brand=brand)
        profile = self.build_profile_from_discovery(discovery_result)

        return discovery_result, profile

    def build_profile_from_discovery(
        self, discovery_result: DiscoveryResult
    ) -> OfficialProductProfile:
        """
        Constructs an OfficialProductProfile baseline from a DiscoveryResult object.
        Deep specification extraction will be populated in Phase 3.
        """
        verified = discovery_result.verified_source
        official_url = verified.url if verified else None
        source_name = verified.provider if verified else "none"

        return OfficialProductProfile(
            brand=discovery_result.brand or "Generic Brand",
            product_name=discovery_result.query,
            normalized_name=discovery_result.normalized_name,
            category="Unassigned",
            official_url=official_url,
            source=source_name,
            confidence=discovery_result.confidence,
            metadata={
                "discovery_status": discovery_result.status,
                "discovery_reasoning": discovery_result.reasoning,
                "candidate_count": len(discovery_result.candidate_sources),
            },
        )

    def validate(self, profile: OfficialProductProfile) -> bool:
        """
        Validates whether a retrieved OfficialProductProfile meets verification thresholds.
        """
        logger.debug(
            f"[ReferenceDiscoveryService] Validate called for profile '{profile.normalized_name}'."
        )
        return profile.confidence > 0.50

    def normalize(self, raw_name: str, brand: str = "") -> str:
        """
        Normalizes raw product title and brand into a canonical lookup string.
        """
        return self.pipeline.normalize_request(query=raw_name, brand=brand)

    def build_profile(self, raw_data: Dict[str, Any]) -> OfficialProductProfile:
        """
        Constructs an OfficialProductProfile from raw external data dictionaries.
        """
        brand = raw_data.get("brand", "Generic Brand")
        name = raw_data.get("product_name", raw_data.get("title", "Unknown Product"))
        return OfficialProductProfile(
            brand=brand,
            product_name=name,
            normalized_name=self.normalize(name, brand),
            category=raw_data.get("category"),
            model_number=raw_data.get("model_number"),
            manufacturer=raw_data.get("manufacturer"),
            official_url=raw_data.get("official_url"),
            official_images=raw_data.get("official_images", []),
            specifications=raw_data.get("specifications", {}),
            colors=raw_data.get("colors", []),
            msrp=raw_data.get("msrp"),
            currency=raw_data.get("currency", "INR"),
            warranty=raw_data.get("warranty"),
            source=raw_data.get("source", "raw_dict_build"),
            confidence=float(raw_data.get("confidence", 0.0)),
            metadata=raw_data.get("metadata", {}),
        )
