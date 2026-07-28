"""
CounterGuard v2.2 — Retail Price Intelligence HTTP Client
Shared async HTTP client with structured metadata extraction (JSON-LD, Open Graph, schema.org).
Provides honest confidence classification: Verified / Estimated / Unavailable.
"""
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTTP Client Configuration
# ---------------------------------------------------------------------------

_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
}

HTTP_TIMEOUT = 6.0  # seconds


# ---------------------------------------------------------------------------
# Confidence Enum
# ---------------------------------------------------------------------------


class PriceConfidence(str, Enum):
    VERIFIED = "Verified"  # Parsed from live structured metadata
    ESTIMATED = "Estimated"  # Heuristic / no live retrieval was possible
    UNAVAILABLE = "Unavailable"  # Live retrieval attempted; price not found


class ExtractionMethod(str, Enum):
    JSON_LD = "JSON-LD (schema.org)"
    OPEN_GRAPH = "Open Graph"
    HTML_SELECTOR = "HTML Selector"
    HEURISTIC = "Heuristic (no live retrieval)"
    NONE = "None"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class RetailPriceResult:
    """
    Fully transparent retail price retrieval result.
    Never confuses estimated values with live-verified facts.
    """

    provider: str
    product_query: str
    retrieval_url: str

    price: Optional[float] = None
    currency: str = "USD"
    title: Optional[str] = None
    availability: Optional[str] = None
    sku: Optional[str] = None

    confidence: PriceConfidence = PriceConfidence.UNAVAILABLE
    extraction_method: ExtractionMethod = ExtractionMethod.NONE
    live_retrieval: bool = False

    http_status: Optional[int] = None
    failure_reason: Optional[str] = None
    latency_ms: float = 0.0
    retrieved_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    content_hash: Optional[str] = None
    response_size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "product_query": self.product_query,
            "retrieval_url": self.retrieval_url,
            "price": self.price,
            "currency": self.currency,
            "title": self.title,
            "availability": self.availability,
            "sku": self.sku,
            "confidence": self.confidence.value,
            "extraction_method": self.extraction_method.value,
            "live_retrieval": self.live_retrieval,
            "http_status": self.http_status,
            "failure_reason": self.failure_reason,
            "latency_ms": self.latency_ms,
            "retrieved_at": self.retrieved_at,
            "content_hash": self.content_hash,
            "response_size_bytes": self.response_size_bytes,
        }


# ---------------------------------------------------------------------------
# Metadata Extractor
# ---------------------------------------------------------------------------


class StructuredMetadataExtractor:
    """
    Extracts product pricing from structured metadata in HTML responses.
    Priority order:
      1. application/ld+json  (schema.org/Product)
      2. Open Graph meta tags  (og:price:amount)
      3. HTML selector patterns  (last resort, brittle)
    """

    @staticmethod
    def extract_json_ld(html: str) -> Optional[Dict[str, Any]]:
        """Parse first schema.org/Product JSON-LD block found in page."""
        pattern = re.compile(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            re.DOTALL | re.IGNORECASE,
        )
        for match in pattern.finditer(html):
            try:
                data = json.loads(match.group(1).strip())
                # Unwrap @graph arrays
                if isinstance(data, dict) and "@graph" in data:
                    for node in data["@graph"]:
                        if isinstance(node, dict) and node.get("@type") in (
                            "Product",
                            "ItemList",
                        ):
                            return node
                if isinstance(data, dict) and data.get("@type") in ("Product",):
                    return data
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            return item
            except (json.JSONDecodeError, ValueError):
                continue
        return None

    @staticmethod
    def price_from_json_ld(data: Dict[str, Any]) -> Optional[float]:
        """Extract price from schema.org Product JSON-LD node."""
        offers = data.get("offers") or data.get("Offers")
        if not offers:
            return None
        if isinstance(offers, list):
            offers = offers[0]
        if isinstance(offers, dict):
            for key in ("price", "lowPrice", "highPrice"):
                val = offers.get(key)
                if val is not None:
                    try:
                        return float(str(val).replace(",", "").replace("$", ""))
                    except (ValueError, TypeError):
                        continue
        return None

    @staticmethod
    def title_from_json_ld(data: Dict[str, Any]) -> Optional[str]:
        return data.get("name")

    @staticmethod
    def availability_from_json_ld(data: Dict[str, Any]) -> Optional[str]:
        offers = data.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        availability = offers.get("availability", "")
        if "InStock" in availability:
            return "In Stock"
        if "OutOfStock" in availability:
            return "Out of Stock"
        return availability or None

    @staticmethod
    def extract_open_graph(html: str) -> Dict[str, Optional[str]]:
        """Extract Open Graph product price meta tags."""
        result: Dict[str, Optional[str]] = {
            "price": None,
            "currency": None,
            "title": None,
        }
        patterns = {
            "price": re.compile(
                r'<meta[^>]+property=["\']og:price:amount["\'][^>]+content=["\']([\d.,]+)["\']',
                re.IGNORECASE,
            ),
            "currency": re.compile(
                r'<meta[^>]+property=["\']og:price:currency["\'][^>]+content=["\']([\w]+)["\']',
                re.IGNORECASE,
            ),
            "title": re.compile(
                r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
                re.IGNORECASE,
            ),
        }
        for key, pat in patterns.items():
            m = pat.search(html)
            if m:
                result[key] = m.group(1).strip()
        return result

    @staticmethod
    def extract_html_price(html: str) -> Optional[float]:
        """Last-resort HTML selector: look for common price microdata patterns."""
        selectors = [
            r'itemprop=["\']price["\'][^>]+content=["\']([\d.,]+)["\']',
            r'class=["\'][^"\']*price[^"\']*["\'][^>]*>\s*\$?([\d,]+\.?\d*)',
            r'"price"\s*:\s*"?([\d]+\.?\d*)"?',
        ]
        for pattern in selectors:
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                try:
                    val = float(m.group(1).replace(",", ""))
                    if 0.01 < val < 99999:  # Sanity check
                        return val
                except (ValueError, TypeError):
                    continue
        return None


# ---------------------------------------------------------------------------
# Live HTTP Retriever
# ---------------------------------------------------------------------------


class RetailHTTPClient:
    """
    Performs genuine async HTTP requests to retailer search/product pages
    and extracts price data via structured metadata.

    Failure modes are first-class outcomes:
      - HTTP timeout       → failure_reason = "HTTP timeout"
      - 403 / anti-bot     → failure_reason = "Blocked (403 / anti-bot protection)"
      - 404                → failure_reason = "Product page not found (404)"
      - Parse failure      → failure_reason = "No structured price metadata found"
      - Exception          → failure_reason = "Network error: <message>"
    """

    def __init__(self, timeout: float = HTTP_TIMEOUT):
        self.timeout = timeout
        self.extractor = StructuredMetadataExtractor()

    def _parse_html_response(
        self,
        html: str,
        provider: str,
        query: str,
        url: str,
        http_status: int,
        latency: float,
        content_hash: str,
        response_size: int,
    ) -> Optional["RetailPriceResult"]:
        """Extract price from HTML using JSON-LD → Open Graph → HTML selector fallback chain."""
        # Priority 1: JSON-LD (schema.org)
        json_ld = self.extractor.extract_json_ld(html)
        if json_ld:
            price = self.extractor.price_from_json_ld(json_ld)
            if price is not None:
                return RetailPriceResult(
                    provider=provider,
                    product_query=query,
                    retrieval_url=url,
                    price=price,
                    title=self.extractor.title_from_json_ld(json_ld),
                    availability=self.extractor.availability_from_json_ld(json_ld),
                    confidence=PriceConfidence.VERIFIED,
                    extraction_method=ExtractionMethod.JSON_LD,
                    live_retrieval=True,
                    http_status=http_status,
                    latency_ms=latency,
                    content_hash=content_hash,
                    response_size_bytes=response_size,
                )

        # Priority 2: Open Graph
        og = self.extractor.extract_open_graph(html)
        if og.get("price"):
            try:
                price = float(str(og["price"]).replace(",", ""))
                return RetailPriceResult(
                    provider=provider,
                    product_query=query,
                    retrieval_url=url,
                    price=price,
                    currency=og.get("currency") or "USD",
                    title=og.get("title"),
                    confidence=PriceConfidence.VERIFIED,
                    extraction_method=ExtractionMethod.OPEN_GRAPH,
                    live_retrieval=True,
                    http_status=http_status,
                    latency_ms=latency,
                    content_hash=content_hash,
                    response_size_bytes=response_size,
                )
            except (ValueError, TypeError):
                pass

        # Priority 3: HTML microdata selectors
        html_price = self.extractor.extract_html_price(html)
        if html_price is not None:
            return RetailPriceResult(
                provider=provider,
                product_query=query,
                retrieval_url=url,
                price=html_price,
                confidence=PriceConfidence.VERIFIED,
                extraction_method=ExtractionMethod.HTML_SELECTOR,
                live_retrieval=True,
                http_status=http_status,
                latency_ms=latency,
                content_hash=content_hash,
                response_size_bytes=response_size,
            )

        return None

    async def fetch_price(
        self,
        provider: str,
        query: str,
        url: str,
        *,
        estimated_fallback: Optional[float] = None,
    ) -> "RetailPriceResult":
        """
        Fetch and parse a retailer page. Returns a fully transparent RetailPriceResult.
        If live retrieval fails and estimated_fallback is provided, returns Estimated confidence.
        Never returns Estimated as if it were Verified.
        """
        start_t = time.time()

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=_REQUEST_HEADERS,
            ) as client:
                response = await client.get(url)

            latency = round((time.time() - start_t) * 1000.0, 1)
            http_status = response.status_code
            html = response.text
            content_hash = (
                "sha256-" + hashlib.sha256(html[:4096].encode()).hexdigest()[:16]
            )
            response_size = len(response.content)

            # --- Handle non-200 status codes ---
            if http_status == 403:
                return self._blocked_result(
                    provider, query, url, http_status, latency, estimated_fallback
                )
            if http_status == 404:
                return RetailPriceResult(
                    provider=provider,
                    product_query=query,
                    retrieval_url=url,
                    confidence=PriceConfidence.UNAVAILABLE,
                    extraction_method=ExtractionMethod.NONE,
                    live_retrieval=True,
                    http_status=404,
                    failure_reason="Product page not found (404)",
                    latency_ms=latency,
                    content_hash=content_hash,
                    response_size_bytes=response_size,
                )
            if http_status != 200:
                return self._blocked_result(
                    provider, query, url, http_status, latency, estimated_fallback
                )

            # Delegate all metadata parsing to helper (resolves C901 complexity)
            parsed = self._parse_html_response(
                html,
                provider,
                query,
                url,
                http_status,
                latency,
                content_hash,
                response_size,
            )
            if parsed is not None:
                return parsed

            return RetailPriceResult(
                provider=provider,
                product_query=query,
                retrieval_url=url,
                confidence=PriceConfidence.UNAVAILABLE,
                extraction_method=ExtractionMethod.NONE,
                live_retrieval=True,
                http_status=http_status,
                failure_reason="No structured price metadata found in response",
                latency_ms=latency,
                content_hash=content_hash,
                response_size_bytes=response_size,
            )

        except httpx.TimeoutException:
            latency = round((time.time() - start_t) * 1000.0, 1)
            return self._failure_result(
                provider, query, url, "HTTP timeout", latency, estimated_fallback
            )

        except httpx.ConnectError as exc:
            latency = round((time.time() - start_t) * 1000.0, 1)
            return self._failure_result(
                provider,
                query,
                url,
                f"Connection error: {exc}",
                latency,
                estimated_fallback,
            )

        except Exception as exc:
            latency = round((time.time() - start_t) * 1000.0, 1)
            return self._failure_result(
                provider,
                query,
                url,
                f"Network error: {exc}",
                latency,
                estimated_fallback,
            )

    def _blocked_result(
        self,
        provider: str,
        query: str,
        url: str,
        http_status: int,
        latency: float,
        estimated_fallback: Optional[float],
    ) -> RetailPriceResult:
        if estimated_fallback is not None:
            return RetailPriceResult(
                provider=provider,
                product_query=query,
                retrieval_url=url,
                price=estimated_fallback,
                confidence=PriceConfidence.ESTIMATED,
                extraction_method=ExtractionMethod.HEURISTIC,
                live_retrieval=False,
                http_status=http_status,
                failure_reason=f"Blocked ({http_status} / anti-bot protection) — price is estimated, not live",
                latency_ms=latency,
            )
        return RetailPriceResult(
            provider=provider,
            product_query=query,
            retrieval_url=url,
            confidence=PriceConfidence.UNAVAILABLE,
            extraction_method=ExtractionMethod.NONE,
            live_retrieval=False,
            http_status=http_status,
            failure_reason=f"Blocked ({http_status} / anti-bot protection)",
            latency_ms=latency,
        )

    def _failure_result(
        self,
        provider: str,
        query: str,
        url: str,
        reason: str,
        latency: float,
        estimated_fallback: Optional[float],
    ) -> RetailPriceResult:
        if estimated_fallback is not None:
            return RetailPriceResult(
                provider=provider,
                product_query=query,
                retrieval_url=url,
                price=estimated_fallback,
                confidence=PriceConfidence.ESTIMATED,
                extraction_method=ExtractionMethod.HEURISTIC,
                live_retrieval=False,
                failure_reason=f"{reason} — price is estimated, not live",
                latency_ms=latency,
            )
        return RetailPriceResult(
            provider=provider,
            product_query=query,
            retrieval_url=url,
            confidence=PriceConfidence.UNAVAILABLE,
            extraction_method=ExtractionMethod.NONE,
            live_retrieval=False,
            failure_reason=reason,
            latency_ms=latency,
        )


# ---------------------------------------------------------------------------
# Multi-Provider Price Consensus
# ---------------------------------------------------------------------------


@dataclass
class PriceConsensus:
    """Aggregate statistics across multiple provider results."""

    providers: List[str] = field(default_factory=list)
    verified_prices: List[float] = field(default_factory=list)
    estimated_prices: List[float] = field(default_factory=list)
    unavailable_providers: List[str] = field(default_factory=list)
    failure_reasons: Dict[str, str] = field(default_factory=dict)

    @property
    def all_prices(self) -> List[float]:
        return self.verified_prices + self.estimated_prices

    @property
    def has_verified(self) -> bool:
        return len(self.verified_prices) > 0

    def minimum(self) -> Optional[float]:
        return min(self.all_prices) if self.all_prices else None

    def maximum(self) -> Optional[float]:
        return max(self.all_prices) if self.all_prices else None

    def average(self) -> Optional[float]:
        if not self.all_prices:
            return None
        return round(sum(self.all_prices) / len(self.all_prices), 2)

    def median(self) -> Optional[float]:
        if not self.all_prices:
            return None
        s = sorted(self.all_prices)
        n = len(s)
        if n % 2 == 0:
            return round((s[n // 2 - 1] + s[n // 2]) / 2, 2)
        return s[n // 2]

    def std_deviation(self) -> Optional[float]:
        if len(self.all_prices) < 2:
            return None
        avg = self.average()
        if avg is None:
            return None
        variance = sum((p - avg) ** 2 for p in self.all_prices) / len(self.all_prices)
        return round(variance**0.5, 2)

    def agreement_score(self) -> float:
        """0.0–1.0 agreement score. 1.0 = all verified providers agree within 5%."""
        if len(self.verified_prices) < 2:
            return 1.0 if self.verified_prices else 0.0
        avg = sum(self.verified_prices) / len(self.verified_prices)
        deviations = [abs(p - avg) / avg for p in self.verified_prices if avg > 0]
        within_5pct = sum(1 for d in deviations if d <= 0.05)
        return round(within_5pct / len(self.verified_prices), 2)

    def overall_confidence(self) -> PriceConfidence:
        if self.verified_prices:
            return PriceConfidence.VERIFIED
        if self.estimated_prices:
            return PriceConfidence.ESTIMATED
        return PriceConfidence.UNAVAILABLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "providers_queried": self.providers,
            "verified_count": len(self.verified_prices),
            "estimated_count": len(self.estimated_prices),
            "unavailable_count": len(self.unavailable_providers),
            "unavailable_providers": self.unavailable_providers,
            "failure_reasons": self.failure_reasons,
            "minimum_price": self.minimum(),
            "maximum_price": self.maximum(),
            "average_price": self.average(),
            "median_price": self.median(),
            "std_deviation": self.std_deviation(),
            "agreement_score": self.agreement_score(),
            "overall_confidence": self.overall_confidence().value,
        }


def build_consensus(results: List[RetailPriceResult]) -> PriceConsensus:
    """Aggregate a list of RetailPriceResults into a PriceConsensus."""
    consensus = PriceConsensus()
    for r in results:
        consensus.providers.append(r.provider)
        if r.confidence == PriceConfidence.VERIFIED and r.price is not None:
            consensus.verified_prices.append(r.price)
        elif r.confidence == PriceConfidence.ESTIMATED and r.price is not None:
            consensus.estimated_prices.append(r.price)
        else:
            consensus.unavailable_providers.append(r.provider)
            if r.failure_reason:
                consensus.failure_reasons[r.provider] = r.failure_reason
    return consensus
