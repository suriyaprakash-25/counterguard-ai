import logging
import re
from typing import Any, Dict, Optional, Tuple

from backend.schemas.official_product import OfficialProductProfile
from backend.schemas.raw_extraction import RawExtractionResult

logger = logging.getLogger(__name__)


class ExtractionNormalizationEngine:
    """
    ExtractionNormalizationEngine (Sprint 17 Phase 3 Preparation)

    Normalizes messy raw extracted strings (e.g. "Battery: 45 mAh", "Battery Size = 45 MAH", "Rs. 4,999")
    into a single canonical `OfficialProductProfile` representation.
    """

    @staticmethod
    def parse_price(price_str: Optional[str]) -> Tuple[Optional[float], str]:
        """
        Extracts numerical float price and currency from raw price strings like '$199.99' or 'Rs. 4,999'.
        """
        if not price_str:
            return None, "INR"

        currency = (
            "USD"
            if "$" in price_str
            else ("INR" if "rs" in price_str.lower() or "₹" in price_str else "INR")
        )
        clean = price_str.replace(",", "")
        match = re.search(r"\d+(?:\.\d+)?", clean)
        val = float(match.group(0)) if match else None
        return val, currency

    def normalize_specifications(self, raw_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes specification keys and values into canonical lower-snake-case dictionaries.
        E.g., "Battery Capacity" -> "battery_capacity": "45 mAh"
        """
        normalized: Dict[str, Any] = {}
        for key, val in raw_specs.items():
            clean_key = (
                re.sub(r"[^\w\s]", "", str(key)).strip().lower().replace(" ", "_")
            )
            val_str = str(val).strip() if val is not None else ""
            normalized[clean_key] = val_str
        return normalized

    def normalize(self, raw: RawExtractionResult) -> OfficialProductProfile:
        """
        Converts a RawExtractionResult into a normalized OfficialProductProfile.
        """
        logger.debug(
            f"[ExtractionNormalizationEngine] Normalizing RawExtractionResult from '{raw.url}'."
        )

        price_val, currency = self.parse_price(raw.raw_price_str)
        norm_specs = self.normalize_specifications(raw.raw_specs)

        raw_title = raw.raw_title or "Unknown Product"
        raw_brand = raw.raw_brand or "Generic Brand"
        normalized_name = f"{raw_brand} {raw_title}".strip().lower()

        return OfficialProductProfile(
            brand=raw_brand,
            product_name=raw_title,
            normalized_name=normalized_name,
            category=norm_specs.get("category", "Unassigned"),
            official_url=raw.url,
            official_images=raw.raw_images,
            specifications=norm_specs,
            msrp=price_val,
            currency=currency,
            warranty=raw.raw_warranty,
            source=raw.provider,
            confidence=raw.confidence,
            evidence_trail=raw.evidence_trail,
            metadata={
                "extraction_method": raw.extraction_method,
                "extraction_time_ms": raw.extraction_time_ms,
                "raw_timestamp": raw.timestamp,
            },
        )
