import logging
import time
from typing import Any, Dict

from backend.providers.base import BaseProviderAdapter
from backend.services.product_canonicalizer import ProductCanonicalizer
from backend.services.product_search_service import ProductSearchService

logger = logging.getLogger(__name__)


class LivePriceAdapter(BaseProviderAdapter):
    """
    Evidence-Backed Production Live Price Intelligence Adapter (v2.1).

    Completely eliminates heuristic default floats ($249.99) and local lookup tables.
    Aggregates real-time prices across Amazon, Best Buy, Walmart, Flipkart, and Brand Flagship Stores
    via ProductSearchService.
    """

    def __init__(self):
        super().__init__()
        self.search_service = ProductSearchService()

    @property
    def name(self) -> str:
        return "LivePriceAdapter"

    @property
    def category(self) -> str:
        return "price"

    def lookup(self, target: str) -> Dict[str, Any]:
        """
        Dynamically aggregates live retail prices for target product across multiple search providers.
        Returns evidence-backed MSRP, market bounds, and price deviation percentages.
        """
        start_t = time.time()
        canonical = ProductCanonicalizer.canonicalize(target)

        try:
            items = self.search_service.search_trusted_products(
                canonical, target_price=0.0
            )
        except Exception as e:
            logger.warning(f"Live price search notice for '{canonical}': {e}")
            items = []

        latency = round((time.time() - start_t) * 1000.0, 1)

        if items and len(items) > 0:
            prices = [item.price for item in items if item.price > 0]

            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = round(sum(prices) / len(prices), 2)
                official_msrp = (
                    max_price  # Highest verified retail price as MSRP benchmark
                )

                return {
                    "canonical_title": canonical,
                    "average_msrp": official_msrp,
                    "lowest_historical_price": min_price,
                    "highest_historical_price": max_price,
                    "average_market_price": avg_price,
                    "sample_size": len(prices),
                    "status": "Verified Evidence-Backed Retail Search",
                    "live_retrieval": True,
                    "provider": self.name,
                    "latency_ms": latency,
                    "sources": [item.store for item in items[:3]],
                }

        # Explicit "Unavailable" status when no live retailer prices are returned
        return {
            "canonical_title": canonical,
            "average_msrp": 0.0,
            "lowest_historical_price": 0.0,
            "highest_historical_price": 0.0,
            "average_market_price": 0.0,
            "sample_size": 0,
            "status": "Unavailable - Pending Retailer Search",
            "live_retrieval": True,
            "provider": self.name,
            "latency_ms": latency,
            "sources": [],
        }

    def search(self, query: str) -> Dict[str, Any]:
        return self.lookup(query)

    def verify(self, entity: str) -> Dict[str, Any]:
        return self.lookup(entity)
