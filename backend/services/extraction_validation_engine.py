import logging
from typing import Tuple

from backend.schemas.official_product import OfficialProductProfile

logger = logging.getLogger(__name__)


class ExtractionValidationEngine:
    """
    ExtractionValidationEngine (Sprint 17 Phase 3 Preparation)

    Validates that a normalized OfficialProductProfile satisfies structural quality thresholds.
    """

    def validate(self, profile: OfficialProductProfile) -> Tuple[bool, str]:
        """
        Validates an OfficialProductProfile for completeness and quality confidence.
        Returns Tuple[is_valid: bool, reasoning: str].
        """
        if not profile:
            return False, "Rejected: Null product profile"

        if not profile.product_name or profile.product_name == "Unknown Product":
            return False, "Rejected: Missing valid product title"

        if not profile.brand or profile.brand == "Generic Brand":
            return False, "Rejected: Unverified brand name"

        if profile.confidence < 0.50:
            return (
                False,
                f"Rejected: Profile confidence ({profile.confidence}) below threshold 0.50",
            )

        return (
            True,
            f"Validated: Profile for '{profile.normalized_name}' passed all structural quality checks",
        )
