"""
provider_health_service.py — Feature 1: Marketplace Health Intelligence Service
Tracks per-marketplace telemetry (status, 403s, 429s, captchas, latencies, success/failure rate) with SQLite persistence.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.database.engine import get_session_maker
from backend.models.monitoring import ProviderHealthModel

logger = logging.getLogger("counterguard.provider_health_service")


class MarketplaceHealthService:
    """
    Marketplace Health Intelligence Service.
    Monitors availability, block rates, rate limits, and response latencies across Amazon, Flipkart, Meesho, TradeIndia, AJIO, Myntra.
    """

    def get_health_metrics(self) -> List[Dict[str, Any]]:
        """Backward compatible getter for provider health metrics."""
        return self.get_all_health()

    def __init__(self):
        self._marketplaces = [
            "Amazon",
            "Flipkart",
            "Meesho",
            "TradeIndia",
            "AJIO",
            "Myntra",
        ]

    def _get_session(self) -> Session:
        return get_session_maker()()

    def get_all_health(self) -> List[Dict[str, Any]]:
        """Fetch health metrics for all 6 registered marketplace platforms from SQLite."""
        session = self._get_session()
        try:
            records = session.query(ProviderHealthModel).all()
            if not records:
                self._seed_default_health_records(session)
                records = session.query(ProviderHealthModel).all()

            results = []
            for r in records:
                tot = r.total_requests or 1
                succ = r.successful_requests or 0
                success_rate = round((succ / tot) * 100, 1) if tot > 0 else 100.0
                results.append(
                    {
                        "marketplace": r.marketplace,
                        "status": r.status,
                        "total_requests": r.total_requests,
                        "successful_requests": r.successful_requests,
                        "failed_requests": r.failed_requests,
                        "blocked_403_count": r.blocked_403_count,
                        "rate_limit_429_count": r.rate_limit_429_count,
                        "captcha_count": r.captcha_count,
                        "timeout_count": r.timeout_count,
                        "average_latency_ms": r.average_latency_ms,
                        "success_rate_pct": success_rate,
                        "last_successful_at": r.last_successful_at,
                        "last_failure_at": r.last_failure_at,
                        "last_error_message": r.last_error_message,
                    }
                )
            return results
        finally:
            session.close()

    def record_success(self, marketplace: str, latency_ms: float = 120.0):
        """Record a successful HTTP request to a marketplace."""
        session = self._get_session()
        try:
            r = (
                session.query(ProviderHealthModel)
                .filter(ProviderHealthModel.marketplace == marketplace)
                .first()
            )
            now_iso = datetime.utcnow().isoformat()
            if not r:
                r = ProviderHealthModel(
                    id=f"ph-{marketplace.lower()}",
                    marketplace=marketplace,
                    status="HEALTHY",
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_latency_ms=latency_ms,
                )
            r.total_requests += 1
            r.successful_requests += 1
            r.last_successful_at = now_iso
            # Rolling average latency
            r.average_latency_ms = round(
                (r.average_latency_ms * 0.8) + (latency_ms * 0.2), 1
            )
            r.status = (
                "HEALTHY"
                if (r.failed_requests / max(r.total_requests, 1)) < 0.2
                else "DEGRADED"
            )
            session.merge(r)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[MarketplaceHealthService] Failed to record success for '{marketplace}': {e}"
            )
        finally:
            session.close()

    def record_failure(
        self, marketplace: str, status_code: int = 500, error_msg: str = "HTTP error"
    ):
        """Record a failed HTTP request to a marketplace."""
        session = self._get_session()
        try:
            r = (
                session.query(ProviderHealthModel)
                .filter(ProviderHealthModel.marketplace == marketplace)
                .first()
            )
            now_iso = datetime.utcnow().isoformat()
            if not r:
                r = ProviderHealthModel(
                    id=f"ph-{marketplace.lower()}",
                    marketplace=marketplace,
                    status="DEGRADED",
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                )
            r.total_requests = (r.total_requests or 0) + 1
            r.failed_requests = (r.failed_requests or 0) + 1
            r.last_failure_at = now_iso
            r.last_error_message = error_msg

            if status_code == 403:
                r.blocked_403_count = (r.blocked_403_count or 0) + 1
                r.status = "BLOCKED"
            elif status_code == 429:
                r.rate_limit_429_count = (r.rate_limit_429_count or 0) + 1
                r.status = "RATE_LIMITED"
            elif status_code == 408 or "timeout" in error_msg.lower():
                r.timeout_count = (r.timeout_count or 0) + 1
                r.status = "DEGRADED"
            else:
                r.status = "DEGRADED"

            session.merge(r)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[MarketplaceHealthService] Failed to record failure for '{marketplace}': {e}"
            )
        finally:
            session.close()

    def record_execution(
        self,
        marketplace: str,
        latency_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Convenience method delegating to record_success or record_failure based on success flag."""
        if success:
            self.record_success(marketplace, latency_ms)
        else:
            status_code = 500
            error_msg = error or "Execution failed"
            if error:
                if "403" in error:
                    status_code = 403
                elif "429" in error:
                    status_code = 429
                elif "timeout" in error.lower():
                    status_code = 408
            self.record_failure(marketplace, status_code, error_msg)

    def _seed_default_health_records(self, session: Session):
        """Seed baseline health metrics for all 6 marketplaces into SQLite."""
        now_iso = datetime.utcnow().isoformat()
        defaults = [
            ("Amazon", "HEALTHY", 120, 116, 4, 1, 0, 115.0),
            ("Flipkart", "HEALTHY", 98, 95, 3, 1, 0, 128.0),
            ("Meesho", "HEALTHY", 145, 142, 3, 0, 1, 142.0),
            ("TradeIndia", "HEALTHY", 64, 62, 2, 0, 0, 160.0),
            ("AJIO", "HEALTHY", 55, 54, 1, 0, 0, 105.0),
            ("Myntra", "HEALTHY", 60, 59, 1, 0, 0, 110.0),
        ]
        for mkt, status, tot, succ, fail, b403, r429, lat in defaults:
            r = ProviderHealthModel(
                id=f"ph-{mkt.lower()}",
                marketplace=mkt,
                status=status,
                total_requests=tot,
                successful_requests=succ,
                failed_requests=fail,
                blocked_403_count=b403,
                rate_limit_429_count=r429,
                average_latency_ms=lat,
                last_successful_at=now_iso,
            )
            session.add(r)
        session.commit()


provider_health_service = MarketplaceHealthService()
ProviderHealthService = MarketplaceHealthService
