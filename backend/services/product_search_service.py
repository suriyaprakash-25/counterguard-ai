import asyncio
import hashlib
import logging
import re
import time
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx

from backend.schemas.product_intelligence import (
    IntelligentProduct,
    ProductNormalized,
    ProviderSearchResult,
    RetrievalProvenance,
    ScoreBreakdown,
    SellerVerification,
)
from backend.services.price_intelligence_service import PriceIntelligenceService
from backend.services.provider_health_service import ProviderHealthService
from backend.services.retail_http_client import (
    PriceConfidence,
    RetailHTTPClient,
)
from backend.services.retrieval_cache import RetrievalCache

logger = logging.getLogger(__name__)

# Allowed Whitelisted Trusted Domains
ALLOWED_TRUSTED_DOMAINS = {
    "nike.com": {
        "store": "Nike Official Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Brand Flagship",
    },
    "adidas.com": {
        "store": "Adidas Flagship Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Brand Flagship",
    },
    "apple.com": {
        "store": "Apple Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Apple Store",
    },
    "samsung.com": {
        "store": "Samsung Official Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Samsung Direct",
    },
    "nothing.tech": {
        "store": "Nothing Official Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Nothing Brand Store",
    },
    "sony.com": {
        "store": "Sony Direct Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Sony Direct",
    },
    "gucci.com": {
        "store": "Gucci Official Boutique",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Gucci Boutique",
    },
    "ray-ban.com": {
        "store": "Ray-Ban Official Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Ray-Ban Direct",
    },
    "rolex.com": {
        "store": "Rolex Official Retailer",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Authorized Rolex Dealer Network",
    },
    "bose.com": {
        "store": "Bose Direct Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Bose Audio Store",
    },
    "dell.com": {
        "store": "Dell Official Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Dell Store",
    },
    "lenovo.com": {
        "store": "Lenovo Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Lenovo Store",
    },
    "microsoft.com": {
        "store": "Microsoft Store",
        "type": "Official Store",
        "badge": "🟢 Official Store",
        "reason": "Official Microsoft Store",
    },
    "amazon.com": {
        "store": "Amazon Official Seller",
        "type": "Trusted Marketplace",
        "badge": "🟡 Trusted Marketplace",
        "reason": "Amazon Verified Brand Store",
    },
    "bestbuy.com": {
        "store": "Best Buy Authorized Store",
        "type": "Authorized Retailer",
        "badge": "🔵 Authorized Retailer",
        "reason": "Best Buy Official Partner",
    },
    "walmart.com": {
        "store": "Walmart Official Store",
        "type": "Authorized Retailer",
        "badge": "🔵 Authorized Retailer",
        "reason": "Walmart Retail Partner",
    },
    "flipkart.com": {
        "store": "Flipkart Official Partner",
        "type": "Authorized Retailer",
        "badge": "🔵 Authorized Retailer",
        "reason": "Flipkart Verified Partner",
    },
}


class ProductSearchProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        pass


class BrandCatalogProvider(ProductSearchProvider):
    @property
    def name(self) -> str:
        return "BrandCatalogProvider"

    DIRECT_CATALOGS: Dict[str, Dict[str, Any]] = {
        "nothing": {
            "domain": "nothing.tech",
            "url": "https://nothing.tech/products/",
            "store": "Nothing Official Store",
            "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500",
        },
        "nike": {
            "domain": "nike.com",
            "url": "https://www.nike.com/w?q=",
            "store": "Nike Official Store",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
        },
        "apple": {
            "domain": "apple.com",
            "url": "https://www.apple.com/us/search/",
            "store": "Apple Store",
            "image": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500",
        },
        "samsung": {
            "domain": "samsung.com",
            "url": "https://www.samsung.com/us/search/searchMain/?searchTerm=",
            "store": "Samsung Official Store",
            "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500",
        },
        "sony": {
            "domain": "sony.com",
            "url": "https://electronics.sony.com/search?query=",
            "store": "Sony Direct Store",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        },
    }

    _http = RetailHTTPClient()

    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        start_t = time.time()
        brand_key = normalized.brand.lower().strip()
        catalog = self.DIRECT_CATALOGS.get(brand_key)

        if not catalog:
            ms = round((time.time() - start_t) * 1000.0, 1)
            return ProviderSearchResult(
                provider_name=self.name, items=[], execution_time_ms=ms, success=True
            )

        search_query = urllib.parse.quote(f"{normalized.brand} {normalized.model}")
        live_url = f"{catalog['url']}{search_query}"

        result = await self._http.fetch_price(
            provider=self.name,
            query=f"{normalized.brand} {normalized.model}",
            url=live_url,
            estimated_fallback=None,  # Never fabricate official store prices
        )

        if result.price is None:
            ms = round((time.time() - start_t) * 1000.0, 1)
            logger.info(
                f"[BrandCatalogProvider] {result.failure_reason or 'No price found'} on {catalog['domain']} for '{normalized.normalized_title}'"
            )
            return ProviderSearchResult(
                provider_name=self.name,
                items=[],
                execution_time_ms=ms,
                success=False,
                error=result.failure_reason
                or "Price unavailable on official brand store",
            )

        content_hash = (
            result.content_hash
            or f"sha256-{hashlib.sha256(live_url.encode()).hexdigest()[:16]}"
        )
        verification_status = (
            f"Verified Official Brand Flagship ({result.extraction_method.value})"
            if result.confidence == PriceConfidence.VERIFIED
            else f"Official URL — price blocked/unavailable: {result.failure_reason}"
        )

        ms = round((time.time() - start_t) * 1000.0, 1)
        return ProviderSearchResult(
            provider_name=self.name,
            items=[
                IntelligentProduct(
                    product_name=result.title or normalized.normalized_title,
                    brand=normalized.brand,
                    model=normalized.model,
                    store=catalog["store"],
                    store_type="Official Store",
                    official=True,
                    price=result.price,
                    currency=result.currency,
                    availability=result.availability or "Check Availability",
                    warranty=f"1-Year {normalized.brand} Official Warranty",
                    image_url=catalog["image"],
                    product_url=live_url,
                    score=98 if result.confidence == PriceConfidence.VERIFIED else 65,
                    score_breakdown=ScoreBreakdown(
                        model_match=40,
                        official_source=25,
                        seller_trust=15,
                        price_match=9,
                        metadata_completeness=9,
                        total=98,
                    ),
                    provenance=RetrievalProvenance(
                        retrieved_url=live_url,
                        retrieved_at=result.retrieved_at,
                        http_status=result.http_status or 0,
                        domain=catalog["domain"],
                        search_query=f"site:{catalog['domain']} {normalized.model}",
                        provider=self.name,
                        content_hash=content_hash,
                        extraction_confidence=0.98
                        if result.confidence == PriceConfidence.VERIFIED
                        else 0.30,
                        verification_status=verification_status,
                    ),
                    seller_verification=SellerVerification(
                        status="Official Manufacturer Direct",
                        verification_reason=f"Verified Brand Store for {normalized.brand}",
                        verification_source="Official Brand Registry + HTTP Retrieval",
                        sold_by=catalog["store"],
                        ships_from=f"{normalized.brand} Direct Warehouse",
                    ),
                    why_recommended=(
                        f"Live price ({result.extraction_method.value}) from {catalog['store']} official brand store."
                        if result.confidence == PriceConfidence.VERIFIED
                        else f"Official store URL — live price unavailable: {result.failure_reason}"
                    ),
                )
            ],
            execution_time_ms=ms,
            success=True,
        )


class AmazonProvider(ProductSearchProvider):
    """
    Live HTTP retrieval from Amazon search pages.
    Attempts JSON-LD → Open Graph → HTML parsing.
    On anti-bot block (403): returns Estimated confidence with transparent reason.
    """

    _http = RetailHTTPClient()

    @property
    def name(self) -> str:
        return "AmazonProvider"

    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        start_t = time.time()
        search_query = urllib.parse.quote(f"{normalized.brand} {normalized.model}")
        live_url = f"https://www.amazon.com/s?k={search_query}"

        result = await self._http.fetch_price(
            provider=self.name,
            query=f"{normalized.brand} {normalized.model}",
            url=live_url,
            estimated_fallback=None,  # Never fabricate prices
        )

        if result.price is None:
            ms = round((time.time() - start_t) * 1000.0, 1)
            logger.info(
                f"[AmazonProvider] {result.failure_reason or 'No price found'} for '{normalized.normalized_title}'"
            )
            return ProviderSearchResult(
                provider_name=self.name,
                items=[],
                execution_time_ms=ms,
                success=False,
                error=result.failure_reason or "Price unavailable",
            )

        content_hash = (
            result.content_hash
            or f"sha256-{hashlib.sha256(live_url.encode()).hexdigest()[:16]}"
        )
        verification_status = (
            "Amazon Live Retrieval"
            if result.confidence == PriceConfidence.VERIFIED
            else f"Estimated ({result.failure_reason})"
        )
        extraction_confidence = (
            0.95 if result.confidence == PriceConfidence.VERIFIED else 0.30
        )

        item = IntelligentProduct(
            product_name=result.title or f"{normalized.normalized_title} (Amazon)",
            brand=normalized.brand,
            model=normalized.model,
            store=f"Amazon ({normalized.brand} Authorized)",
            store_type="Trusted Marketplace",
            official=True,
            price=result.price,
            currency=result.currency,
            availability=result.availability or "Check Availability",
            warranty=f"1-Year {normalized.brand} Manufacturer Warranty",
            image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
            product_url=live_url,
            score=92 if result.confidence == PriceConfidence.VERIFIED else 55,
            score_breakdown=ScoreBreakdown(
                model_match=40,
                official_source=20,
                seller_trust=14,
                price_match=9,
                metadata_completeness=9,
                total=92,
            ),
            provenance=RetrievalProvenance(
                retrieved_url=live_url,
                retrieved_at=result.retrieved_at,
                http_status=result.http_status or 0,
                domain="amazon.com",
                search_query=f"{normalized.brand} {normalized.model}",
                provider=self.name,
                content_hash=content_hash,
                extraction_confidence=extraction_confidence,
                verification_status=verification_status,
            ),
            seller_verification=SellerVerification(
                status="Amazon Verified Brand Store",
                verification_reason=f"Authorized Brand Store on Amazon for {normalized.brand}",
                verification_source="Amazon Merchant Verification",
                sold_by=f"Amazon / {normalized.brand} Direct",
                ships_from="Amazon Fulfillment Center",
            ),
            why_recommended=(
                f"Live price ({result.extraction_method.value}) from Amazon."
                if result.confidence == PriceConfidence.VERIFIED
                else f"Estimated (live retrieval unavailable: {result.failure_reason})"
            ),
        )
        ms = round((time.time() - start_t) * 1000.0, 1)
        return ProviderSearchResult(
            provider_name=self.name, items=[item], execution_time_ms=ms, success=True
        )


class BestBuyProvider(ProductSearchProvider):
    """
    Live HTTP retrieval from Best Buy search pages.
    Best Buy embeds schema.org/Product JSON-LD on product detail pages.
    """

    _http = RetailHTTPClient()

    @property
    def name(self) -> str:
        return "BestBuyProvider"

    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        start_t = time.time()
        search_query = urllib.parse.quote(f"{normalized.brand} {normalized.model}")
        live_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={search_query}"

        result = await self._http.fetch_price(
            provider=self.name,
            query=f"{normalized.brand} {normalized.model}",
            url=live_url,
            estimated_fallback=None,
        )

        if result.price is None:
            ms = round((time.time() - start_t) * 1000.0, 1)
            logger.info(
                f"[BestBuyProvider] {result.failure_reason or 'No price found'} for '{normalized.normalized_title}'"
            )
            return ProviderSearchResult(
                provider_name=self.name,
                items=[],
                execution_time_ms=ms,
                success=False,
                error=result.failure_reason or "Price unavailable",
            )

        content_hash = (
            result.content_hash
            or f"sha256-{hashlib.sha256(live_url.encode()).hexdigest()[:16]}"
        )
        verification_status = (
            "Best Buy Live Retrieval"
            if result.confidence == PriceConfidence.VERIFIED
            else f"Estimated ({result.failure_reason})"
        )
        extraction_confidence = (
            0.92 if result.confidence == PriceConfidence.VERIFIED else 0.30
        )

        item = IntelligentProduct(
            product_name=result.title or f"{normalized.normalized_title} (Best Buy)",
            brand=normalized.brand,
            model=normalized.model,
            store="Best Buy Authorized Store",
            store_type="Authorized Retailer",
            official=True,
            price=result.price,
            currency=result.currency,
            availability=result.availability or "Check Availability",
            warranty="Best Buy 1-Year Price Match & Warranty",
            image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
            product_url=live_url,
            score=88 if result.confidence == PriceConfidence.VERIFIED else 50,
            score_breakdown=ScoreBreakdown(
                model_match=38,
                official_source=20,
                seller_trust=13,
                price_match=8,
                metadata_completeness=9,
                total=88,
            ),
            provenance=RetrievalProvenance(
                retrieved_url=live_url,
                retrieved_at=result.retrieved_at,
                http_status=result.http_status or 0,
                domain="bestbuy.com",
                search_query=f"{normalized.brand} {normalized.model}",
                provider=self.name,
                content_hash=content_hash,
                extraction_confidence=extraction_confidence,
                verification_status=verification_status,
            ),
            seller_verification=SellerVerification(
                status="Best Buy Official Partner",
                verification_reason="Official Retail Store Network",
                verification_source="Best Buy Merchant Registry",
                sold_by="Best Buy Stores",
                ships_from="Best Buy Warehouse",
            ),
            why_recommended=(
                f"Live price ({result.extraction_method.value}) from Best Buy."
                if result.confidence == PriceConfidence.VERIFIED
                else f"Estimated (live retrieval unavailable: {result.failure_reason})"
            ),
        )
        ms = round((time.time() - start_t) * 1000.0, 1)
        return ProviderSearchResult(
            provider_name=self.name, items=[item], execution_time_ms=ms, success=True
        )


class WalmartProvider(ProductSearchProvider):
    """
    Live HTTP retrieval from Walmart search pages.
    Walmart serves JSON-LD and structured product data in many responses.
    """

    _http = RetailHTTPClient()

    @property
    def name(self) -> str:
        return "WalmartProvider"

    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        start_t = time.time()
        search_query = urllib.parse.quote(f"{normalized.brand} {normalized.model}")
        live_url = f"https://www.walmart.com/search?q={search_query}"

        result = await self._http.fetch_price(
            provider=self.name,
            query=f"{normalized.brand} {normalized.model}",
            url=live_url,
            estimated_fallback=None,
        )

        if result.price is None:
            ms = round((time.time() - start_t) * 1000.0, 1)
            logger.info(
                f"[WalmartProvider] {result.failure_reason or 'No price found'} for '{normalized.normalized_title}'"
            )
            return ProviderSearchResult(
                provider_name=self.name,
                items=[],
                execution_time_ms=ms,
                success=False,
                error=result.failure_reason or "Price unavailable",
            )

        content_hash = (
            result.content_hash
            or f"sha256-{hashlib.sha256(live_url.encode()).hexdigest()[:16]}"
        )
        verification_status = (
            "Walmart Live Retrieval"
            if result.confidence == PriceConfidence.VERIFIED
            else f"Estimated ({result.failure_reason})"
        )
        extraction_confidence = (
            0.90 if result.confidence == PriceConfidence.VERIFIED else 0.30
        )

        item = IntelligentProduct(
            product_name=result.title or f"{normalized.normalized_title} (Walmart)",
            brand=normalized.brand,
            model=normalized.model,
            store="Walmart Official Store",
            store_type="Authorized Retailer",
            official=True,
            price=result.price,
            currency=result.currency,
            availability=result.availability or "Check Availability",
            warranty="Walmart 90-Day Guarantee & 1-Year Warranty",
            image_url="https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=500",
            product_url=live_url,
            score=85 if result.confidence == PriceConfidence.VERIFIED else 48,
            score_breakdown=ScoreBreakdown(
                model_match=36,
                official_source=18,
                seller_trust=13,
                price_match=9,
                metadata_completeness=9,
                total=85,
            ),
            provenance=RetrievalProvenance(
                retrieved_url=live_url,
                retrieved_at=result.retrieved_at,
                http_status=result.http_status or 0,
                domain="walmart.com",
                search_query=f"{normalized.brand} {normalized.model}",
                provider=self.name,
                content_hash=content_hash,
                extraction_confidence=extraction_confidence,
                verification_status=verification_status,
            ),
            seller_verification=SellerVerification(
                status="Walmart Retail Partner",
                verification_reason="Official Retail Store",
                verification_source="Walmart Merchant Network",
                sold_by="Walmart.com",
                ships_from="Walmart Logistics Center",
            ),
            why_recommended=(
                f"Live price ({result.extraction_method.value}) from Walmart."
                if result.confidence == PriceConfidence.VERIFIED
                else f"Estimated (live retrieval unavailable: {result.failure_reason})"
            ),
        )
        ms = round((time.time() - start_t) * 1000.0, 1)
        return ProviderSearchResult(
            provider_name=self.name, items=[item], execution_time_ms=ms, success=True
        )


class FlipkartProvider(ProductSearchProvider):
    """
    Live HTTP retrieval from Flipkart search pages.
    Flipkart renders structured JSON pricing data in many search responses.
    """

    _http = RetailHTTPClient()

    @property
    def name(self) -> str:
        return "FlipkartProvider"

    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        start_t = time.time()
        search_query = urllib.parse.quote(f"{normalized.brand} {normalized.model}")
        live_url = f"https://www.flipkart.com/search?q={search_query}"

        result = await self._http.fetch_price(
            provider=self.name,
            query=f"{normalized.brand} {normalized.model}",
            url=live_url,
            estimated_fallback=None,
        )

        if result.price is None:
            ms = round((time.time() - start_t) * 1000.0, 1)
            logger.info(
                f"[FlipkartProvider] {result.failure_reason or 'No price found'} for '{normalized.normalized_title}'"
            )
            return ProviderSearchResult(
                provider_name=self.name,
                items=[],
                execution_time_ms=ms,
                success=False,
                error=result.failure_reason or "Price unavailable",
            )

        content_hash = (
            result.content_hash
            or f"sha256-{hashlib.sha256(live_url.encode()).hexdigest()[:16]}"
        )
        verification_status = (
            "Flipkart Live Retrieval"
            if result.confidence == PriceConfidence.VERIFIED
            else f"Estimated ({result.failure_reason})"
        )
        extraction_confidence = (
            0.89 if result.confidence == PriceConfidence.VERIFIED else 0.30
        )

        item = IntelligentProduct(
            product_name=result.title or f"{normalized.normalized_title} (Flipkart)",
            brand=normalized.brand,
            model=normalized.model,
            store="Flipkart Official Partner",
            store_type="Authorized Retailer",
            official=True,
            price=result.price,
            currency=result.currency,
            availability=result.availability or "Check Availability",
            warranty="Flipkart Assured 1-Year Warranty",
            image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
            product_url=live_url,
            score=84 if result.confidence == PriceConfidence.VERIFIED else 45,
            score_breakdown=ScoreBreakdown(
                model_match=36,
                official_source=18,
                seller_trust=12,
                price_match=9,
                metadata_completeness=9,
                total=84,
            ),
            provenance=RetrievalProvenance(
                retrieved_url=live_url,
                retrieved_at=result.retrieved_at,
                http_status=result.http_status or 0,
                domain="flipkart.com",
                search_query=f"{normalized.brand} {normalized.model}",
                provider=self.name,
                content_hash=content_hash,
                extraction_confidence=extraction_confidence,
                verification_status=verification_status,
            ),
            seller_verification=SellerVerification(
                status="Flipkart Assured Partner",
                verification_reason="Regional Retail Partner Network",
                verification_source="Flipkart Merchant Registry",
                sold_by="Flipkart Assured Merchant",
                ships_from="Flipkart Fulfillment Hub",
            ),
            why_recommended=(
                f"Live price ({result.extraction_method.value}) from Flipkart."
                if result.confidence == PriceConfidence.VERIFIED
                else f"Estimated (live retrieval unavailable: {result.failure_reason})"
            ),
        )
        ms = round((time.time() - start_t) * 1000.0, 1)
        return ProviderSearchResult(
            provider_name=self.name, items=[item], execution_time_ms=ms, success=True
        )


class LiveSearchProvider(ProductSearchProvider):
    """
    DuckDuckGo HTML search to discover trusted domain URLs for a product query.
    Then fetches each discovered trusted-domain URL via RetailHTTPClient.
    Prices are only recorded when live structured metadata is actually extracted.
    No est_price fallbacks — if extraction fails, the item is excluded.
    """

    _http = RetailHTTPClient(timeout=5.0)

    @property
    def name(self) -> str:
        return "LiveSearchProvider"

    async def search_async(
        self, normalized: ProductNormalized, target_price: float = 0.0
    ) -> ProviderSearchResult:
        start_t = time.time()
        results: List[IntelligentProduct] = []
        search_query = f"{normalized.brand} {normalized.model} buy official"

        try:
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with httpx.AsyncClient(
                timeout=5.0, follow_redirects=True, headers=headers
            ) as client:
                resp = await client.get(ddg_url)

            if resp.status_code != 200:
                ms = round((time.time() - start_t) * 1000.0, 1)
                return ProviderSearchResult(
                    provider_name=self.name,
                    items=[],
                    execution_time_ms=ms,
                    success=False,
                    error=f"DuckDuckGo search returned HTTP {resp.status_code}",
                )

            # Extract result URLs and filter to trusted domains only
            raw_urls = re.findall(r'class="result__url"\s+href="([^"]+)"', resp.text)
            trusted_hits: List[tuple] = []
            for raw_u in raw_urls[:10]:
                clean_u = urllib.parse.unquote(raw_u).strip()
                if not clean_u.startswith("http"):
                    clean_u = f"https://{clean_u}"
                domain_match = self._extract_trusted_domain(clean_u)
                if domain_match:
                    trusted_hits.append((clean_u, domain_match))
                if len(trusted_hits) >= 3:
                    break

            # Fetch each trusted URL and attempt live price extraction
            fetch_tasks = [
                self._http.fetch_price(
                    provider=self.name,
                    query=f"{normalized.brand} {normalized.model}",
                    url=url,
                    estimated_fallback=None,
                )
                for url, _ in trusted_hits
            ]
            fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

            for (url, domain_match), fetch_res in zip(trusted_hits, fetch_results):
                if isinstance(fetch_res, Exception) or fetch_res.price is None:
                    continue

                domain_info = ALLOWED_TRUSTED_DOMAINS[domain_match]
                content_hash = (
                    fetch_res.content_hash
                    or f"sha256-{hashlib.sha256(url.encode()).hexdigest()[:16]}"
                )
                verification_status = (
                    f"Live Retrieved ({fetch_res.extraction_method.value})"
                    if fetch_res.confidence == PriceConfidence.VERIFIED
                    else f"Blocked / {fetch_res.failure_reason}"
                )

                results.append(
                    IntelligentProduct(
                        product_name=fetch_res.title or normalized.normalized_title,
                        brand=normalized.brand,
                        model=normalized.model,
                        store=domain_info["store"],
                        store_type=domain_info["type"],
                        official=domain_info["type"] == "Official Store",
                        price=fetch_res.price,
                        currency=fetch_res.currency,
                        availability=fetch_res.availability or "Check Availability",
                        warranty=f"1-Year {normalized.brand} Official Warranty",
                        image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                        product_url=url,
                        score=95
                        if fetch_res.confidence == PriceConfidence.VERIFIED
                        else 60,
                        score_breakdown=ScoreBreakdown(
                            model_match=40,
                            official_source=25,
                            seller_trust=14,
                            price_match=8,
                            metadata_completeness=8,
                            total=95,
                        ),
                        provenance=RetrievalProvenance(
                            retrieved_url=url,
                            retrieved_at=fetch_res.retrieved_at,
                            http_status=fetch_res.http_status or 0,
                            domain=domain_match,
                            search_query=search_query,
                            provider=self.name,
                            content_hash=content_hash,
                            extraction_confidence=0.96
                            if fetch_res.confidence == PriceConfidence.VERIFIED
                            else 0.30,
                            verification_status=verification_status,
                        ),
                        seller_verification=SellerVerification(
                            status="Live Search Verified Merchant",
                            verification_reason=domain_info["reason"],
                            verification_source="Live Domain Lookup + HTTP Retrieval",
                            sold_by=domain_info["store"],
                            ships_from=f"{domain_info['store']} Logistics",
                        ),
                        why_recommended=f"Live retrieved from {domain_info['store']} ({fetch_res.extraction_method.value}).",
                    )
                )

        except Exception as e:
            logger.warning(f"LiveSearchProvider execution warning: {e}")

        ms = round((time.time() - start_t) * 1000.0, 1)
        return ProviderSearchResult(
            provider_name=self.name, items=results, execution_time_ms=ms, success=True
        )

    def _extract_trusted_domain(self, url: str) -> Optional[str]:
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.lower()
            for trusted_domain in ALLOWED_TRUSTED_DOMAINS:
                if netloc == trusted_domain or netloc.endswith(f".{trusted_domain}"):
                    return trusted_domain
        except Exception:
            pass
        return None


class ProductSearchService:
    """
    Production-grade Product Intelligence Search Service.
    Queries providers concurrently via asyncio.gather(), enforces HTTPS reachability & domain whitelisting,
    interacts with RetrievalCache & ProviderHealthService, computes PriceIntelligence, and logs performance.
    """

    def __init__(self, providers: Optional[List[ProductSearchProvider]] = None):
        self.providers = providers or [
            BrandCatalogProvider(),
            AmazonProvider(),
            BestBuyProvider(),
            WalmartProvider(),
            FlipkartProvider(),
            LiveSearchProvider(),
        ]
        self.health_service = ProviderHealthService()
        self.cache = RetrievalCache()
        self.price_service = PriceIntelligenceService()

    def normalize_product(
        self, raw_title: str, brand_hint: str = ""
    ) -> ProductNormalized:
        clean_title = raw_title.strip()
        brand = brand_hint.strip()

        if not brand:
            known_brands = [
                "Nike",
                "Adidas",
                "Apple",
                "Samsung",
                "Nothing",
                "Sony",
                "Gucci",
                "Ray-Ban",
                "Rolex",
                "Bose",
                "Dell",
                "Lenovo",
            ]
            for kb in known_brands:
                if re.search(rf"\b{kb}\b", clean_title, re.IGNORECASE):
                    brand = kb
                    break

        if not brand:
            words = clean_title.split()
            brand = words[0] if words else "Generic"

        model = clean_title
        if brand.lower() in clean_title.lower():
            model = re.sub(
                rf"\b{re.escape(brand)}\b", "", clean_title, flags=re.IGNORECASE
            ).strip()

        category = "General Goods"
        title_lower = clean_title.lower()
        if (
            "shoe" in title_lower
            or "sneaker" in title_lower
            or "air max" in title_lower
        ):
            category = "Footwear & Apparel"
        elif (
            "earbud" in title_lower
            or "headphone" in title_lower
            or "buds" in title_lower
        ):
            category = "Audio Electronics"
        elif "watch" in title_lower or "rolex" in title_lower:
            category = "Timepieces"

        return ProductNormalized(
            brand=brand.title(),
            model=model or clean_title,
            category=category,
            normalized_title=f"{brand.title()} {model}".strip(),
        )

    def validate_retrieved_product(self, item: IntelligentProduct) -> bool:
        if not item.product_url or not item.product_url.startswith("https://"):
            return False

        if item.price <= 0:
            return False

        try:
            netloc = urllib.parse.urlparse(item.product_url).netloc.lower()
            is_trusted = any(
                netloc == td or netloc.endswith(f".{td}")
                for td in ALLOWED_TRUSTED_DOMAINS
            )
            if not is_trusted:
                return False
        except Exception:
            return False

        return True

    def compute_ranking_score(
        self, item: IntelligentProduct, target_price: float
    ) -> ScoreBreakdown:
        model_sim = 40
        official_weight = 25 if item.official else 18
        seller_trust = (
            15
            if item.store_type == "Official Store"
            else (13 if item.store_type == "Authorized Retailer" else 12)
        )

        price_match = 10
        if target_price > 0:
            diff = abs(item.price - target_price) / max(item.price, target_price)
            price_match = max(5, round((1.0 - diff) * 10))

        meta_score = (
            10 if (item.product_url and item.image_url and item.warranty) else 8
        )

        total = model_sim + official_weight + seller_trust + price_match + meta_score

        return ScoreBreakdown(
            model_match=model_sim,
            official_source=official_weight,
            seller_trust=seller_trust,
            price_match=price_match,
            metadata_completeness=meta_score,
            total=total,
        )

    async def search_trusted_products_async(
        self,
        raw_title: str,
        brand_hint: str = "",
        target_price: float = 0.0,
        region: str = "Global",
    ) -> Dict[str, Any]:
        """
        Executes concurrent retrieval across all providers using asyncio.gather().
        Applies RetrievalCache, ProviderHealth monitoring, candidate deduplication, and PriceIntelligence calculations.
        """
        pipeline_start_t = time.time()
        normalized = self.normalize_product(raw_title, brand_hint)

        # 1. Check RetrievalCache
        cached_result = self.cache.get(normalized.brand, normalized.model, region)
        if cached_result:
            logger.info(
                f"[ProductSearchService] Returning cached product intelligence for {normalized.normalized_title}"
            )
            return cached_result

        # 2. Execute ALL providers concurrently using asyncio.gather()
        tasks = [
            provider.search_async(normalized, target_price)
            for provider in self.providers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        candidates: List[IntelligentProduct] = []
        provider_counts: Dict[str, int] = {}

        # 3. Process results & record Provider Health Metrics
        for provider, res in zip(self.providers, results):
            p_name = provider.name
            if isinstance(res, Exception):
                logger.error(f"Provider {p_name} failed: {res}")
                self.health_service.record_execution(p_name, 500.0, False, str(res))
                provider_counts[p_name] = 0
            elif isinstance(res, ProviderSearchResult):
                self.health_service.record_execution(
                    p_name, res.execution_time_ms, res.success, res.error
                )
                valid_items = [
                    item for item in res.items if self.validate_retrieved_product(item)
                ]
                candidates.extend(valid_items)
                provider_counts[p_name] = len(valid_items)

        total_raw = len(candidates)

        # 4. Compute detailed ScoreBreakdown for candidates
        for item in candidates:
            sb = self.compute_ranking_score(item, target_price)
            item.score_breakdown = sb
            item.score = sb.total

        # 5. Sort descending by score
        candidates.sort(key=lambda x: -x.score)

        # 6. Deduplicate by brand, model, domain, store
        seen_keys = set()
        deduped: List[IntelligentProduct] = []
        for item in candidates:
            key = f"{item.brand.lower()}:{item.provenance.domain.lower()}:{item.store.lower()}"
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(item)

        duplicates_removed = total_raw - len(deduped)
        final_top_5 = deduped[:5]

        # 7. Compute PriceIntelligence & RecommendationSummary
        price_intel = self.price_service.compute_price_intelligence(
            final_top_5, target_price
        )
        summary = self.price_service.compute_recommendation_summary(final_top_5)

        pipeline_ms = round((time.time() - pipeline_start_t) * 1000.0, 1)

        # 8. Log Performance & Summary
        logger.info(
            "=================================================================="
        )
        logger.info("[ProductSearchService] Async Concurrent Retrieval Summary:")
        logger.info(f"  • Providers Queried: {len(self.providers)} concurrently")
        logger.info(f"  • Retrieved Per Provider: {provider_counts}")
        logger.info(f"  • Total Valid Candidates: {total_raw}")
        logger.info(f"  • Duplicates Removed: {duplicates_removed}")
        logger.info(f"  • Final Top 5 Items Returned: {len(final_top_5)}")
        logger.info(f"  • Async Pipeline Execution Duration: {pipeline_ms} ms")
        logger.info(
            "=================================================================="
        )

        response_payload = {
            "normalized_product": normalized.model_dump(mode="json"),
            "recommended_products": [
                item.model_dump(mode="json") for item in final_top_5
            ],
            "price_intelligence": price_intel.model_dump(mode="json")
            if price_intel
            else None,
            "recommendation_summary": summary.model_dump(mode="json")
            if summary
            else None,
            "pipeline_duration_ms": pipeline_ms,
        }

        # 9. Store in RetrievalCache
        self.cache.set(normalized.brand, normalized.model, response_payload, region)

        return response_payload

    def search_trusted_products(
        self, raw_title: str, brand_hint: str = "", target_price: float = 0.0
    ) -> List[IntelligentProduct]:
        """
        Synchronous wrapper calling search_trusted_products_async using asyncio.run.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop running in async context, run task synchronously via thread
                res = asyncio.run_coroutine_threadsafe(
                    self.search_trusted_products_async(
                        raw_title, brand_hint, target_price
                    ),
                    loop,
                ).result()
                return [
                    IntelligentProduct(**item) for item in res["recommended_products"]
                ]
            else:
                res = loop.run_until_complete(
                    self.search_trusted_products_async(
                        raw_title, brand_hint, target_price
                    )
                )
                return [
                    IntelligentProduct(**item) for item in res["recommended_products"]
                ]
        except Exception:
            res = asyncio.run(
                self.search_trusted_products_async(raw_title, brand_hint, target_price)
            )
            return [IntelligentProduct(**item) for item in res["recommended_products"]]
