import logging
import re
from typing import Optional, Tuple

from bs4 import BeautifulSoup

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class PriceExtractor(FieldExtractor):
    """
    Production PriceExtractor.
    Extracts raw price strings with currency symbols (₹, $, €, £, INR, USD) using:
      1. OpenGraph price meta tags (og:price:amount, product:price:amount) [0.95]
      2. Price DOM classes (.price, .product-price, [data-price], .money) [0.90]
      3. Page-wide currency regex pattern matching [0.80]
      4. Metadata fallback [0.75]
    """

    PRICE_PATTERN = re.compile(
        r"(?:₹|\$|€|£|INR|USD|EUR|GBP)\s*[\d,]+(?:\.\d{2})?|[\d,]+(?:\.\d{2})?\s*(?:₹|\$|€|£|INR|USD|EUR|GBP)",
        re.IGNORECASE,
    )

    @property
    def target_field(self) -> str:
        return "price"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[str], Optional[ExtractionEvidence]]:
        if not raw_content:
            price_str = candidate.metadata.get("raw_price_str")
            if price_str:
                ev = ExtractionEvidence(
                    field=self.target_field,
                    value=price_str,
                    css_selector="metadata.raw_price_str",
                    source_url=candidate.url,
                    provider=candidate.provider,
                    confidence=candidate.confidence,
                )
                return price_str, ev
            return None, None

        soup = BeautifulSoup(raw_content, "html.parser")

        # 1. OpenGraph price meta tag
        og_price = (
            soup.find("meta", property="og:price:amount")
            or soup.find("meta", property="product:price:amount")
            or soup.find("meta", attrs={"name": "price"})
        )
        if og_price and og_price.get("content"):
            amount = og_price["content"].strip()
            curr_meta = soup.find("meta", property="og:price:currency") or soup.find(
                "meta", property="product:price:currency"
            )
            curr = (
                curr_meta["content"].strip()
                if curr_meta and curr_meta.get("content")
                else "INR"
            )
            raw_p = f"{curr} {amount}"
            ev = ExtractionEvidence(
                field=self.target_field,
                value=raw_p,
                css_selector="meta[property='og:price:amount']",
                xpath="//meta[@property='og:price:amount']/@content",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=0.95,
            )
            return raw_p, ev

        # 2. Price DOM classes
        price_elem = (
            soup.find(class_=re.compile(r"price|money|amount", re.I))
            or soup.find(attrs={"data-price": True})
            or soup.find(id=re.compile(r"price", re.I))
        )
        if price_elem and price_elem.get_text(strip=True):
            elem_text = price_elem.get_text(strip=True)
            match = self.PRICE_PATTERN.search(elem_text)
            if match:
                raw_p = match.group(0)
                ev = ExtractionEvidence(
                    field=self.target_field,
                    value=raw_p,
                    css_selector=f".{price_elem.get('class', ['price'])[0]}",
                    source_url=candidate.url,
                    provider=candidate.provider,
                    confidence=0.90,
                )
                return raw_p, ev

        # 3. Fallback metadata
        meta_price = candidate.metadata.get("raw_price_str")
        if meta_price:
            ev = ExtractionEvidence(
                field=self.target_field,
                value=meta_price,
                css_selector="metadata.raw_price_str",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=0.75,
            )
            return meta_price, ev

        return None, None
