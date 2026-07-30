import csv
import io
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/providers", tags=["Providers"])

logger = logging.getLogger(__name__)


@router.get("/health")
def get_provider_health():
    """GET /api/v1/providers/health — Returns marketplace health metrics."""
    from backend.services.provider_health_service import provider_health_service

    return {"providers": provider_health_service.get_all_health()}


@router.get("/rate-limits")
def get_provider_rate_limits():
    """GET /api/v1/providers/rate-limits — Returns rate limit quotas and circuit breaker states."""
    from backend.services.marketplace_retry_engine import marketplace_retry_engine

    return marketplace_retry_engine.get_rate_limiter_summary()


@router.get("/parser-metrics")
def get_parser_metrics():
    """GET /api/v1/providers/parser-metrics — Returns DOM parser & selector extraction telemetry."""
    from backend.services.parser_metrics_service import parser_metrics_service

    return parser_metrics_service.get_metrics_summary()


@router.get("/archive")
def list_raw_evidence_archives(limit: int = Query(default=50, ge=1, le=200)):
    """GET /api/v1/providers/archive — List recent raw evidence archive entries with SHA-256 hashes."""
    from backend.services.evidence_archive_service import evidence_archive_service

    records = evidence_archive_service.get_all_archives(limit=limit)
    return {"archives": records, "count": len(records)}


@router.get("/archive/{archive_id}")
def get_raw_evidence_archive(archive_id: str):
    """GET /api/v1/providers/archive/{archive_id} — Fetch raw evidence metadata."""
    from backend.services.evidence_archive_service import evidence_archive_service

    data = evidence_archive_service.get_archive(archive_id)
    if not data:
        raise HTTPException(
            status_code=404, detail=f"Archive '{archive_id}' not found."
        )
    return data


@router.get("/export/health-report")
def export_provider_health_csv():
    """GET /api/v1/providers/export/health-report — Export marketplace provider health as CSV."""
    from backend.services.provider_health_service import provider_health_service

    providers = provider_health_service.get_all_health()

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "marketplace",
            "status",
            "total_requests",
            "successful_requests",
            "failed_requests",
            "blocked_403_count",
            "rate_limit_429_count",
            "average_latency_ms",
            "success_rate_pct",
            "last_successful_at",
            "last_error_message",
        ],
    )
    writer.writeheader()
    for p in providers:
        writer.writerow(
            {
                "marketplace": p.get("marketplace", ""),
                "status": p.get("status", ""),
                "total_requests": p.get("total_requests", 0),
                "successful_requests": p.get("successful_requests", 0),
                "failed_requests": p.get("failed_requests", 0),
                "blocked_403_count": p.get("blocked_403_count", 0),
                "rate_limit_429_count": p.get("rate_limit_429_count", 0),
                "average_latency_ms": p.get("average_latency_ms", 0),
                "success_rate_pct": p.get("success_rate_pct", 0),
                "last_successful_at": p.get("last_successful_at", ""),
                "last_error_message": p.get("last_error_message", ""),
            }
        )

    csv_content = output.getvalue()
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=CounterGuard_Provider_Health.csv"
        },
    )


@router.get("/parser-inspector")
def get_parser_inspector():
    """GET /api/v1/providers/parser-inspector — Feature 9 & 13: Live marketplace parser telemetry & rejected diagnostics."""
    from backend.services.parser_metrics_service import parser_metrics_service

    return {"parsers": parser_metrics_service.get_inspector_data()}


@router.get("/parser-history")
def get_parser_history(limit: int = Query(default=50, ge=1, le=200)):
    """GET /api/v1/providers/parser-history — Feature 13: Paginated parser execution history records."""
    from backend.services.parser_metrics_service import parser_metrics_service

    records = parser_metrics_service.get_parser_history(limit=limit)
    return {"history": records, "count": len(records)}


@router.get("/runtime-metrics")
def get_runtime_performance_metrics():
    """GET /api/v1/providers/runtime-metrics — Feature 8 & 13: Pipeline stage performance telemetry (Avg, Min, Max, P95)."""
    from backend.services.performance_metrics_service import performance_metrics_service

    return performance_metrics_service.get_runtime_metrics_summary()
