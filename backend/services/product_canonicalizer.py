import re
import urllib.parse
from typing import Dict, Optional


class ProductCanonicalizer:
    """
    Production-Grade Product Title & Brand Canonicalization Engine.

    Normalizes raw search strings, messy marketplace listing titles, and
    unformatted query parameters into standardized, canonical brand and product names.

    Examples:
        wh1000xm5 / wh-1000xm5     -> Sony WH-1000XM5
        cmf buds 2a / cmf+buds+2a -> Nothing CMF Buds 2a
        iphone 15 pro max        -> Apple iPhone 15 Pro Max
        galaxy s25 ultra         -> Samsung Galaxy S25 Ultra
        airpods pro 2            -> Apple AirPods Pro (2nd Gen)
    """

    # Canonical Brand Registry with aliases
    BRAND_ALIASES: Dict[str, str] = {
        "sony": "Sony",
        "apple": "Apple",
        "samsung": "Samsung",
        "nothing": "Nothing",
        "cmf": "Nothing",
        "bose": "Bose",
        "sennheiser": "Sennheiser",
        "anker": "Anker",
        "soundcore": "Anker",
        "nike": "Nike",
        "adidas": "Adidas",
        "logitech": "Logitech",
        "jbl": "JBL",
        "dyson": "Dyson",
        "canon": "Canon",
        "nikon": "Nikon",
        "dell": "Dell",
        "hp": "HP",
        "lenovo": "Lenovo",
        "asus": "ASUS",
    }

    # Model specific canonical overrides
    CANONICAL_MODELS: Dict[str, str] = {
        "wh1000xm5": "Sony WH-1000XM5 Wireless Headphones",
        "wh-1000xm5": "Sony WH-1000XM5 Wireless Headphones",
        "wh1000xm4": "Sony WH-1000XM4 Noise-Canceling Headphones",
        "wh-1000xm4": "Sony WH-1000XM4 Noise-Canceling Headphones",
        "wf1000xm5": "Sony WF-1000XM5 Wireless Earbuds",
        "cmf buds 2a": "Nothing CMF Buds 2a",
        "cmf buds": "Nothing CMF Buds",
        "nothing phone 2a": "Nothing Phone (2a)",
        "nothing phone 2": "Nothing Phone (2)",
        "iphone 15 pro max": "Apple iPhone 15 Pro Max",
        "iphone 15 pro": "Apple iPhone 15 Pro",
        "iphone 15": "Apple iPhone 15",
        "iphone 14 pro max": "Apple iPhone 14 Pro Max",
        "airpods pro 2": "Apple AirPods Pro (2nd Gen)",
        "airpods max": "Apple AirPods Max",
        "galaxy s25 ultra": "Samsung Galaxy S25 Ultra",
        "galaxy s24 ultra": "Samsung Galaxy S24 Ultra",
        "galaxy s24": "Samsung Galaxy S24",
        "galaxy buds 3 pro": "Samsung Galaxy Buds3 Pro",
        "bose quietcomfort ultra": "Bose QuietComfort Ultra Headphones",
        "bose qc45": "Bose QuietComfort 45 Headphones",
    }

    @classmethod
    def decode_raw_text(cls, raw: str) -> str:
        """URL decode and clean basic whitespace/encoding artifacts."""
        if not raw:
            return ""
        try:
            decoded = urllib.parse.unquote_plus(raw)
        except Exception:
            decoded = raw
        return decoded.replace("+", " ").strip()

    @classmethod
    def canonicalize(  # noqa: C901
        cls,
        raw_title: str,
        brand_hint: Optional[str] = None,
        product_hint: Optional[str] = None,
    ) -> str:
        """
        Main canonicalization entry point. Accepts raw title, search query, or URL slug,
        and returns a standardized, human-readable product name.
        """
        title = cls.decode_raw_text(raw_title)

        # Remove common marketplace noise words & tracking prefix/suffixes
        title_clean = re.sub(
            r"(?i)\b(s\?k=|dp/|gp/product/|search\?q=|assessment|investigation)\b",
            "",
            title,
        ).strip()
        title_clean = re.sub(r"\s+", " ", title_clean)

        title_lower = title_clean.lower()

        # 1. Exact or substring match against Canonical Model Registry
        for key, canonical_name in cls.CANONICAL_MODELS.items():
            if key in title_lower or key.replace("-", "") in title_lower.replace(
                "-", ""
            ):
                return canonical_name

        # 2. Extract brand from hint or title
        detected_brand = None
        if brand_hint and brand_hint.lower() in cls.BRAND_ALIASES:
            detected_brand = cls.BRAND_ALIASES[brand_hint.lower()]
        else:
            for b_alias, b_canonical in cls.BRAND_ALIASES.items():
                if re.search(rf"\b{re.escape(b_alias)}\b", title_lower):
                    detected_brand = b_canonical
                    break

        # 3. Clean up title tokens
        cleaned_tokens = []
        for word in title_clean.split():
            w_lower = word.lower()
            # If word is a brand alias, capitalize properly
            if w_lower in cls.BRAND_ALIASES:
                cleaned_tokens.append(cls.BRAND_ALIASES[w_lower])
            elif re.match(r"^[a-z]{1,3}\d{3,5}[a-z]?$", w_lower):
                # Model code like WH1000XM5 -> WH-1000XM5
                cleaned_tokens.append(word.upper())
            elif word.isupper() and len(word) <= 5:
                cleaned_tokens.append(word)
            else:
                cleaned_tokens.append(word.capitalize())

        result = " ".join(cleaned_tokens).strip()

        # Ensure detected brand is prefixed if missing
        if detected_brand and not result.lower().startswith(detected_brand.lower()):
            result = f"{detected_brand} {result}"

        # If result is empty or too short, fallback to product_hint or generic
        if not result or len(result) < 2:
            if product_hint:
                return product_hint.strip().title()
            return "Verified Product Target"

        return result
