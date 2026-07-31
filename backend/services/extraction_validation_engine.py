import logging
from typing import List, Tuple

from backend.schemas.official_product import OfficialProductProfile

logger = logging.getLogger(__name__)


class ExtractionValidationEngine:
    """
    Production ExtractionValidationEngine.
    Validates normalized OfficialProductProfile quality, computes numerical quality_score (0.0 to 1.0),
    detects missing fields, logs warnings, and sets validation status ('valid', 'partial', 'invalid').
    """

    def validate(self, profile: OfficialProductProfile) -> Tuple[bool, str]:
        """
        Validates an OfficialProductProfile for completeness and quality confidence.
        Returns Tuple[is_valid: bool, reasoning: str].
        """
        if not profile:
            return False, "Rejected: Null product profile"

        missing_fields: List[str] = []
        warnings: List[str] = []
        earned_points = 0
        total_points = 5

        # Field 1: Title (Weight 1)
        if profile.product_name and profile.product_name != "Unknown Product":
            earned_points += 1
        else:
            missing_fields.append("product_name")

        # Field 2: Brand (Weight 1)
        if profile.brand and profile.brand != "Generic Brand":
            earned_points += 1
        else:
            missing_fields.append("brand")

        # Field 3: MSRP / Price (Weight 1)
        if profile.msrp and profile.msrp > 0:
            earned_points += 1
        else:
            missing_fields.append("msrp")
            warnings.append("MSRP numeric price missing or zero.")

        # Field 4: Images (Weight 1)
        if profile.official_images and len(profile.official_images) > 0:
            earned_points += 1
        else:
            missing_fields.append("official_images")

        # Field 5: Specifications (Weight 1)
        if profile.specifications and len(profile.specifications) > 0:
            earned_points += 1
        else:
            missing_fields.append("specifications")

        quality_score = round(earned_points / total_points, 2)
        profile.metadata["quality_score"] = quality_score
        profile.metadata["missing_fields"] = missing_fields
        profile.metadata["warnings"] = warnings

        if quality_score >= 0.60 and "product_name" not in missing_fields:
            status = "valid"
            is_valid = True
        elif quality_score >= 0.40:
            status = "partial"
            is_valid = True
        else:
            status = "invalid"
            is_valid = False

        profile.metadata["validation_status"] = status
        reason = f"Status '{status}': Quality score {quality_score}/1.00. Missing fields: {missing_fields}"
        return is_valid, reason
