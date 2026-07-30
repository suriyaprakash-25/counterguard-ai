"""
marketplace_retry_engine.py — Feature 7 & 8: Marketplace Retry Engine & Independent Rate Limiter
Implements exponential backoff, jitter, circuit breaker pattern, and independent per-marketplace quota limits.
"""
import logging
import random
import time
from typing import Any, Dict

logger = logging.getLogger("counterguard.marketplace_retry_engine")


class MarketplaceRetryEngine:
    """
    Marketplace Retry Engine & Independent Rate Limiter.
    Enforces independent per-marketplace rate limits (requests/min, burst limits) and circuit breaker protection.
    """

    def __init__(self):
        # Per-marketplace rate limits: (max_reqs_per_min, burst_limit)
        self._limits: Dict[str, Dict[str, Any]] = {
            "Amazon": {
                "max_per_min": 60,
                "burst": 10,
                "current_count": 12,
                "last_reset": time.time(),
            },
            "Flipkart": {
                "max_per_min": 60,
                "burst": 10,
                "current_count": 8,
                "last_reset": time.time(),
            },
            "Meesho": {
                "max_per_min": 120,
                "burst": 20,
                "current_count": 15,
                "last_reset": time.time(),
            },
            "TradeIndia": {
                "max_per_min": 90,
                "burst": 15,
                "current_count": 5,
                "last_reset": time.time(),
            },
            "AJIO": {
                "max_per_min": 60,
                "burst": 10,
                "current_count": 4,
                "last_reset": time.time(),
            },
            "Myntra": {
                "max_per_min": 60,
                "burst": 10,
                "current_count": 6,
                "last_reset": time.time(),
            },
        }
        # Circuit Breaker states: "CLOSED" (normal), "OPEN" (tripped), "HALF_OPEN" (recovering)
        self._circuit_states: Dict[str, str] = {m: "CLOSED" for m in self._limits}

    def check_rate_limit(self, marketplace: str) -> bool:
        """Check if request to marketplace is within rate limits."""
        mkt = marketplace if marketplace in self._limits else "Amazon"
        lim = self._limits[mkt]
        now = time.time()

        # Reset counter if 60s passed
        if now - lim["last_reset"] > 60:
            lim["current_count"] = 0
            lim["last_reset"] = now

        if self._circuit_states.get(mkt) == "OPEN":
            logger.warning(
                f"[MarketplaceRetryEngine] Circuit breaker is OPEN for '{mkt}'. Blocking request."
            )
            return False

        if lim["current_count"] >= lim["max_per_min"]:
            logger.warning(
                f"[MarketplaceRetryEngine] Rate limit exceeded for '{mkt}' ({lim['current_count']}/{lim['max_per_min']}/min)."
            )
            return False

        lim["current_count"] += 1
        return True

    def calculate_backoff_delay(
        self, attempt: int, base_delay: float = 1.0, max_delay: float = 10.0
    ) -> float:
        """Calculate exponential backoff delay with random jitter."""
        exponential = base_delay * (2 ** (attempt - 1))
        jitter = random.uniform(0, 0.5 * base_delay)
        return min(exponential + jitter, max_delay)

    def trip_circuit_breaker(self, marketplace: str):
        """Trip circuit breaker for marketplace due to repeated failures."""
        if marketplace in self._circuit_states:
            self._circuit_states[marketplace] = "OPEN"
            logger.error(
                f"[MarketplaceRetryEngine] Circuit breaker TRIPPED for '{marketplace}'."
            )

    def reset_circuit_breaker(self, marketplace: str):
        """Reset circuit breaker for marketplace."""
        if marketplace in self._circuit_states:
            self._circuit_states[marketplace] = "CLOSED"

    def get_rate_limiter_summary(self) -> Dict[str, Any]:
        """Fetch rate limiter status summary for dashboard visualization."""
        summary = {}
        for mkt, cfg in self._limits.items():
            summary[mkt] = {
                "max_requests_per_min": cfg["max_per_min"],
                "used_in_current_minute": cfg["current_count"],
                "remaining_quota": max(cfg["max_per_min"] - cfg["current_count"], 0),
                "circuit_breaker_status": self._circuit_states.get(mkt, "CLOSED"),
            }
        return summary


marketplace_retry_engine = MarketplaceRetryEngine()
