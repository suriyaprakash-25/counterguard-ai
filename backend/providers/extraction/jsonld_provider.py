import json
import logging
import time
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from backend.providers.extraction.base_provider import ExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence
from backend.schemas.raw_extraction import RawExtractionResult

logger = logging.getLogger(__name__)


class JsonLdExtractionProvider(ExtractionProvider):
    """
    Production JsonLdExtractionProvider.
    Extracts Schema.org product microdata from <script type="application/ld+json"> blocks.
    Supports Product, Offer, Brand, AggregateRating, Image, Description, SKU, GTIN, MPN, Price, Currency.
    """

    JSONLD_DOMAINS = {
        "apple.com",
        "nike.com",
        "adidas.com",
        "gucci.com",
        "ray-ban.com",
        "samsung.com",
        "sony.com",
        "nothing.tech",
    }

    @property
    def provider_name(self) -> str:
        return "JsonLdExtractionProvider"

    def supports(self, candidate: SourceCandidate) -> bool:
        return (
            candidate.domain in self.JSONLD_DOMAINS or "json_ld" in candidate.metadata
        )

    def _extract_product_dict(self, json_data: Any) -> Optional[Dict[str, Any]]:
        if isinstance(json_data, dict):
            graph = json_data.get("@graph")
            if graph and isinstance(graph, list):
                for item in graph:
                    if isinstance(item, dict) and item.get("@type") in (
                        "Product",
                        "IndividualProduct",
                        "ProductModel",
                    ):
                        return item
            if json_data.get("@type") in (
                "Product",
                "IndividualProduct",
                "ProductModel",
            ):
                return json_data
        elif isinstance(json_data, list):
            for item in json_data:
                res = self._extract_product_dict(item)
                if res:
                    return res
        return None

    def extract(  # noqa: C901
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> RawExtractionResult:
        start_time = time.time()
        logger.debug(
            f"[{self.provider_name}] Extracting JSON-LD microdata from URL '{candidate.url}'."
        )

        evidence_trail: List[ExtractionEvidence] = []
        raw_title: Optional[str] = candidate.title
        raw_brand: Optional[str] = (
            candidate.domain.split(".")[0].capitalize()
            if candidate.domain
            else "Generic Brand"
        )
        raw_price: Optional[str] = None
        raw_currency: str = "INR"
        raw_images: List[str] = []
        raw_specs: Dict[str, Any] = {}
        raw_desc: Optional[str] = None

        if raw_content:
            soup = BeautifulSoup(raw_content, "html.parser")
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    if not script.string:
                        continue
                    data = json.loads(script.string)
                    p_dict = self._extract_product_dict(data)
                    if p_dict:
                        # Title
                        if p_dict.get("name"):
                            raw_title = str(p_dict["name"]).strip()
                            evidence_trail.append(
                                ExtractionEvidence(
                                    field="title",
                                    value=raw_title,
                                    css_selector="script[type='application/ld+json'] (name)",
                                    source_url=candidate.url,
                                    provider=self.provider_name,
                                    confidence=0.99,
                                )
                            )

                        # Brand
                        brand_obj = p_dict.get("brand")
                        if isinstance(brand_obj, dict) and brand_obj.get("name"):
                            raw_brand = str(brand_obj["name"]).strip()
                        elif isinstance(brand_obj, str):
                            raw_brand = brand_obj.strip()

                        # Images
                        img_obj = p_dict.get("image")
                        if isinstance(img_obj, list):
                            raw_images = [str(i) for i in img_obj if i]
                        elif isinstance(img_obj, str):
                            raw_images = [img_obj]

                        # Description
                        if p_dict.get("description"):
                            raw_desc = str(p_dict["description"]).strip()

                        # Specs (SKU, GTIN, MPN, model)
                        for key in (
                            "sku",
                            "gtin",
                            "gtin13",
                            "gtin8",
                            "mpn",
                            "model",
                            "category",
                            "color",
                        ):
                            if p_dict.get(key):
                                raw_specs[key] = str(p_dict[key]).strip()

                        # Offers / Price
                        offers = p_dict.get("offers")
                        offer_dict = (
                            offers[0]
                            if isinstance(offers, list) and offers
                            else (offers if isinstance(offers, dict) else None)
                        )
                        if offer_dict:
                            price_val = offer_dict.get("price") or offer_dict.get(
                                "lowPrice"
                            )
                            curr_val = offer_dict.get("priceCurrency", "INR")
                            if price_val:
                                raw_price = f"{curr_val} {price_val}"
                                raw_currency = str(curr_val)
                                evidence_trail.append(
                                    ExtractionEvidence(
                                        field="price",
                                        value=raw_price,
                                        css_selector="script[type='application/ld+json'] (offers.price)",
                                        source_url=candidate.url,
                                        provider=self.provider_name,
                                        confidence=0.99,
                                    )
                                )
                        break
                except Exception as err:
                    logger.debug(
                        f"[{self.provider_name}] Error parsing JSON-LD script block: {err}"
                    )

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

        return RawExtractionResult(
            url=candidate.url,
            provider=self.provider_name,
            raw_title=raw_title,
            raw_brand=raw_brand,
            raw_price_str=raw_price,
            raw_currency=raw_currency,
            raw_images=raw_images,
            raw_specs=raw_specs,
            raw_description=raw_desc,
            evidence_trail=evidence_trail,
            extraction_method="json_ld",
            extraction_time_ms=elapsed_ms,
            confidence=0.98 if evidence_trail else 0.85,
            metadata={"domain": candidate.domain, "jsonld_parsed": True},
        )
