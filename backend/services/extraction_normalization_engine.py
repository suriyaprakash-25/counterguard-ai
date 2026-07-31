import logging
import re
from typing import Any, Dict, Optional, Tuple

from backend.schemas.official_product import OfficialProductProfile
from backend.schemas.raw_extraction import RawExtractionResult

logger = logging.getLogger(__name__)


class ExtractionNormalizationEngine:
    """
    Production ExtractionNormalizationEngine.
    Converts messy raw extracted strings (e.g. "Battery Size = 45 MAH", "Rs. 4,999")
    into canonical normalized representations:
      - Canonical specification keys (battery_capacity, display_size, storage, memory, weight, dimensions)
      - Standardized units (mAh, GB, inches, grams)
      - Parsed floating-point MSRP and ISO currency code (INR, USD, EUR)
    """

    KEY_ALIASES: Dict[str, str] = {
        "battery": "battery_capacity",
        "battery_size": "battery_capacity",
        "battery_capacity": "battery_capacity",
        "screen_size": "display_size",
        "display": "display_size",
        "display_size": "display_size",
        "internal_memory": "storage",
        "ram_memory": "memory",
        "ram": "memory",
        "mass": "weight",
    }

    @staticmethod
    def parse_price(price_str: Optional[str]) -> Tuple[Optional[float], str]:
        """
        Extracts numerical float price and currency from raw price strings like '$199.99' or 'Rs. 4,999'.
        """
        if not price_str:
            return None, "INR"

        p_upper = price_str.upper()
        currency = (
            "USD"
            if "$" in price_str or "USD" in p_upper
            else (
                "EUR"
                if "€" in price_str or "EUR" in p_upper
                else ("GBP" if "£" in price_str or "GBP" in p_upper else "INR")
            )
        )
        clean = price_str.replace(",", "")
        match = re.search(r"\d+(?:\.\d+)?", clean)
        val = float(match.group(0)) if match else None
        return val, currency

    def normalize_unit(self, val_str: str) -> str:
        """Standardizes unit strings."""
        val = str(val_str).strip()
        # Battery mAh
        val = re.sub(r"(\d+)\s*mah\b", r"\1 mAh", val, flags=re.I)
        # Storage GB/TB
        val = re.sub(r"(\d+)\s*gb\b", r"\1 GB", val, flags=re.I)
        val = re.sub(r"(\d+)\s*tb\b", r"\1 TB", val, flags=re.I)
        # Weight grams/kg
        val = re.sub(r"(\d+)\s*g\b", r"\1 grams", val, flags=re.I)
        val = re.sub(r"(\d+)\s*kg\b", r"\1 kg", val, flags=re.I)
        return val

    def normalize_specifications(self, raw_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes specification keys into canonical snake_case representations and formats units.
        """
        normalized: Dict[str, Any] = {}
        for key, val in raw_specs.items():
            raw_k_clean = (
                re.sub(r"[^\w\s]", "", str(key)).strip().lower().replace(" ", "_")
            )
            canonical_k = self.KEY_ALIASES.get(raw_k_clean, raw_k_clean)
            val_norm = self.normalize_unit(str(val)) if val is not None else ""
            normalized[canonical_k] = val_norm
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
