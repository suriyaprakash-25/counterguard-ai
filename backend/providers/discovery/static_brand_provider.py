import logging
import urllib.parse
from typing import Any, Dict, List

from backend.providers.discovery.base_provider import SearchProvider
from backend.schemas.discovery_engine import SourceCandidate

logger = logging.getLogger(__name__)


class StaticBrandProvider(SearchProvider):
    """
    StaticBrandProvider (Sprint 17 Phase 2 Deliverable)

    Wraps the existing production hardcoded brand catalog mapping into the new `SearchProvider` interface.
    Preserves exact existing discovery URLs and classifications with zero behavioral change.
    """

    DIRECT_CATALOGS: Dict[str, Dict[str, Any]] = {
        "nothing": {
            "domain": "nothing.tech",
            "url": "https://nothing.tech/products/",
            "store": "Nothing Official Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "nike": {
            "domain": "nike.com",
            "url": "https://www.nike.com/w?q=",
            "store": "Nike Official Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "apple": {
            "domain": "apple.com",
            "url": "https://www.apple.com/us/search/",
            "store": "Apple Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "samsung": {
            "domain": "samsung.com",
            "url": "https://www.samsung.com/us/search/searchMain/?searchTerm=",
            "store": "Samsung Official Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "sony": {
            "domain": "sony.com",
            "url": "https://electronics.sony.com/search?query=",
            "store": "Sony Direct Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "adidas": {
            "domain": "adidas.com",
            "url": "https://www.adidas.com/us/search?q=",
            "store": "Adidas Flagship Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "gucci": {
            "domain": "gucci.com",
            "url": "https://www.gucci.com/us/en/search?search-text=",
            "store": "Gucci Official Boutique",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "ray-ban": {
            "domain": "ray-ban.com",
            "url": "https://www.ray-ban.com/usa/search?text=",
            "store": "Ray-Ban Official Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "rolex": {
            "domain": "rolex.com",
            "url": "https://www.rolex.com/en-us/search?q=",
            "store": "Rolex Official Retailer",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "bose": {
            "domain": "bose.com",
            "url": "https://www.bose.com/search?q=",
            "store": "Bose Direct Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "dell": {
            "domain": "dell.com",
            "url": "https://www.dell.com/en-us/search/",
            "store": "Dell Official Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "lenovo": {
            "domain": "lenovo.com",
            "url": "https://www.lenovo.com/us/en/search?fq=&text=",
            "store": "Lenovo Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "microsoft": {
            "domain": "microsoft.com",
            "url": "https://www.microsoft.com/en-us/search/explore?q=",
            "store": "Microsoft Store",
            "type": "Official Store",
            "confidence": 0.98,
        },
        "amazon": {
            "domain": "amazon.com",
            "url": "https://www.amazon.com/s?k=",
            "store": "Amazon Verified Brand Store",
            "type": "Trusted Marketplace",
            "confidence": 0.85,
        },
        "bestbuy": {
            "domain": "bestbuy.com",
            "url": "https://www.bestbuy.com/site/searchpage.jsp?st=",
            "store": "Best Buy Authorized Store",
            "type": "Authorized Retailer",
            "confidence": 0.90,
        },
        "walmart": {
            "domain": "walmart.com",
            "url": "https://www.walmart.com/search?q=",
            "store": "Walmart Official Store",
            "type": "Authorized Retailer",
            "confidence": 0.90,
        },
        "flipkart": {
            "domain": "flipkart.com",
            "url": "https://www.flipkart.com/search?q=",
            "store": "Flipkart Official Partner",
            "type": "Authorized Retailer",
            "confidence": 0.88,
        },
    }

    @property
    def provider_name(self) -> str:
        return "StaticBrandProvider"

    def search(self, query: str, brand: str = "") -> List[SourceCandidate]:
        logger.debug(
            f"[{self.provider_name}] Executing static search for query='{query}', brand='{brand}'."
        )
        candidates: List[SourceCandidate] = []

        brand_key = (brand or "").strip().lower()
        if not brand_key and query:
            # Extract first word of query as potential brand hint
            brand_key = query.strip().split()[0].lower()

        catalog = self.DIRECT_CATALOGS.get(brand_key)
        if catalog:
            encoded_q = urllib.parse.quote(query)
            target_url = f"{catalog['url']}{encoded_q}"
            candidates.append(
                SourceCandidate(
                    title=f"{catalog['store']} - {query}",
                    url=target_url,
                    source_type=catalog["type"],
                    provider=self.provider_name,
                    confidence=catalog["confidence"],
                    metadata={
                        "domain": catalog["domain"],
                        "store_name": catalog["store"],
                        "brand_key": brand_key,
                    },
                )
            )

        return candidates

    def supports(self, brand: str, domain: str = "") -> bool:
        clean_brand = (brand or "").strip().lower()
        clean_domain = (domain or "").strip().lower()

        if clean_brand in self.DIRECT_CATALOGS:
            return True

        if clean_domain:
            for cat in self.DIRECT_CATALOGS.values():
                if cat["domain"] in clean_domain:
                    return True
        return False

    def health_check(self) -> bool:
        return True
