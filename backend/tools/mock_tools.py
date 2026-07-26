"""
Mock tool implementations for CounterGuard Platform Engineering framework testing and development.
These implement simulated responses without connecting to live external APIs.
"""

from typing import Any, Dict

from backend.exceptions import ToolExecutionError
from backend.tools.base_tool import BaseTool
from backend.tools.tool_registry import ToolRegistry


@ToolRegistry.register()
class MockMarketplaceAPITool(BaseTool):
    """
    Mock implementation of a Marketplace API tool for product and seller verification.
    """

    @property
    def name(self) -> str:
        return "marketplace_api"

    @property
    def description(self) -> str:
        return "Queries e-commerce marketplace APIs for product listing metadata, seller ratings, and pricing history."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "listing_id": {
                    "type": "string",
                    "description": "The unique product or listing ID to query.",
                },
                "marketplace": {
                    "type": "string",
                    "description": "Target platform (e.g., 'amazon', 'ebay', 'walmart').",
                    "default": "amazon",
                },
            },
            "required": ["listing_id"],
        }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        listing_id = kwargs.get("listing_id")
        if not listing_id:
            raise ToolExecutionError(
                "MockMarketplaceAPITool requires a 'listing_id' argument."
            )

        marketplace = kwargs.get("marketplace", "amazon").lower()

        return {
            "listing_id": listing_id,
            "marketplace": marketplace,
            "status": "active",
            "title": f"Simulated Product Title for {listing_id}",
            "current_price": 49.99,
            "currency": "USD",
            "seller_info": {
                "seller_id": f"SELLER_{listing_id[:4]}",
                "reputation_score": 4.6,
                "total_reviews": 312,
                "verified_merchant": True,
            },
            "flags": []
            if "suspicious" not in str(listing_id).lower()
            else ["potential_counterfeit", "price_anomaly"],
        }


@ToolRegistry.register()
class MockBrandRegistryTool(BaseTool):
    """
    Mock implementation of a Brand Registry verification tool.
    """

    @property
    def name(self) -> str:
        return "brand_registry"

    @property
    def description(self) -> str:
        return "Checks global brand trademark databases and verified reseller registries to confirm authorization."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "description": "Name of the brand or trademark to check.",
                },
                "seller_name": {
                    "type": "string",
                    "description": "Optional name of the seller to check for authorized reseller status.",
                },
            },
            "required": ["brand_name"],
        }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        brand_name = kwargs.get("brand_name")
        if not brand_name:
            raise ToolExecutionError(
                "MockBrandRegistryTool requires a 'brand_name' argument."
            )

        seller_name = kwargs.get("seller_name", "")
        is_authorized = not (
            "unauthorized" in str(seller_name).lower()
            or "fake" in str(seller_name).lower()
        )

        return {
            "brand_name": brand_name,
            "trademark_registered": True,
            "registration_number": f"TM-{len(brand_name) * 10042}",
            "owner_entity": f"{brand_name} Global IP Holdings Ltd.",
            "seller_checked": seller_name or None,
            "is_authorized_reseller": is_authorized if seller_name else None,
            "verification_confidence": 0.98,
        }


@ToolRegistry.register()
class MockGoogleSearchTool(BaseTool):
    """
    Mock implementation of a Google Search tool for web open-source intelligence (OSINT).
    """

    @property
    def name(self) -> str:
        return "google_search"

    @property
    def description(self) -> str:
        return "Executes general web search queries to gather open-source intelligence on products, domains, or sellers."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query string."},
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return.",
                    "default": 3,
                },
            },
            "required": ["query"],
        }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        query = kwargs.get("query")
        if not query:
            raise ToolExecutionError(
                "MockGoogleSearchTool requires a 'query' argument."
            )

        num_results = int(kwargs.get("num_results", 3))

        results = []
        for idx in range(1, num_results + 1):
            results.append(
                {
                    "title": f"Search Result {idx}: Information regarding '{query}'",
                    "url": f"https://example.com/search?q={query}&result={idx}",
                    "snippet": f"This is a simulated web search snippet providing evidence and details related to {query} (Source #{idx}).",
                }
            )

        return {
            "query": query,
            "total_matches_estimate": 14200,
            "results": results,
        }


@ToolRegistry.register()
class MockExchangeRatesTool(BaseTool):
    """
    Mock implementation of an Exchange Rates tool for international pricing conversion and variance checks.
    """

    @property
    def name(self) -> str:
        return "exchange_rates"

    @property
    def description(self) -> str:
        return "Retrieves foreign currency exchange rates to evaluate cross-border pricing discrepancies."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "base_currency": {
                    "type": "string",
                    "description": "Base currency code (e.g., 'USD').",
                    "default": "USD",
                },
                "target_currency": {
                    "type": "string",
                    "description": "Target currency code (e.g., 'EUR', 'GBP', 'CNY').",
                },
                "amount": {
                    "type": "number",
                    "description": "Optional amount to convert.",
                    "default": 1.0,
                },
            },
            "required": ["target_currency"],
        }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        target = kwargs.get("target_currency")
        if not target:
            raise ToolExecutionError(
                "MockExchangeRatesTool requires a 'target_currency' argument."
            )

        base = kwargs.get("base_currency", "USD").upper()
        target = target.upper()
        amount = float(kwargs.get("amount", 1.0))

        mock_rates_to_usd = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "CNY": 7.23,
            "JPY": 155.40,
            "CAD": 1.36,
            "AUD": 1.51,
        }

        base_in_usd = mock_rates_to_usd.get(base, 1.0)
        target_in_usd = mock_rates_to_usd.get(target, 1.25)
        rate = round(target_in_usd / base_in_usd, 4)

        return {
            "base_currency": base,
            "target_currency": target,
            "rate": rate,
            "original_amount": amount,
            "converted_amount": round(amount * rate, 2),
            "timestamp_utc": "2026-07-26T12:00:00Z",
        }


@ToolRegistry.register()
class MockReverseImageSearchTool(BaseTool):
    """
    Mock implementation of a Reverse Image Search tool for counterfeit visual matching.
    """

    @property
    def name(self) -> str:
        return "reverse_image_search"

    @property
    def description(self) -> str:
        return "Performs reverse image searches on product photos to detect unauthorized stock photo usage or replica listings."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the product image to check.",
                },
                "similarity_threshold": {
                    "type": "number",
                    "description": "Minimum visual similarity score (0.0 to 1.0).",
                    "default": 0.80,
                },
            },
            "required": ["image_url"],
        }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        image_url = kwargs.get("image_url")
        if not image_url:
            raise ToolExecutionError(
                "MockReverseImageSearchTool requires an 'image_url' argument."
            )

        threshold = float(kwargs.get("similarity_threshold", 0.80))

        matches = [
            {
                "matched_url": "https://official-brand-store.com/assets/original_product.jpg",
                "domain": "official-brand-store.com",
                "similarity_score": 0.99,
                "description": "Official brand manufacturer product catalog image.",
            },
            {
                "matched_url": "https://suspicious-discount-deals.net/img_copy.png",
                "domain": "suspicious-discount-deals.net",
                "similarity_score": 0.94,
                "description": "Unverified third-party discount storefront.",
            },
        ]

        filtered_matches = [m for m in matches if m["similarity_score"] >= threshold]

        return {
            "queried_image_url": image_url,
            "matches_found": len(filtered_matches),
            "similarity_threshold": threshold,
            "matches": filtered_matches,
            "assessment": "High duplication detected across authorized and unauthorized domains.",
        }
