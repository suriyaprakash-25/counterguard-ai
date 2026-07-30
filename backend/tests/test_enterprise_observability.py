"""
test_enterprise_observability.py — Pytest suite for Enterprise Observability, Evidence Provenance, Marketplace Health, and Deep Health APIs.
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.services.evidence_archive_service import evidence_archive_service
from backend.services.marketplace_retry_engine import marketplace_retry_engine
from backend.services.parser_metrics_service import parser_metrics_service
from backend.services.provider_health_service import provider_health_service
from backend.services.retrieval_confidence_engine import retrieval_confidence_engine

client = TestClient(app)


def test_marketplace_health_service():
    """Verify MarketplaceHealthService tracking and SQLite records."""
    health_list = provider_health_service.get_all_health()
    assert len(health_list) >= 6
    mkts = [h["marketplace"] for h in health_list]
    assert "Amazon" in mkts
    assert "Flipkart" in mkts

    # Record success & failure
    provider_health_service.record_success("Amazon", latency_ms=110.0)
    provider_health_service.record_failure(
        "Flipkart", status_code=403, error_msg="Anti-bot challenge"
    )

    updated = provider_health_service.get_all_health()
    fk = next(h for h in updated if h["marketplace"] == "Flipkart")
    assert fk["blocked_403_count"] >= 1


def test_evidence_archive_service():
    """Verify EvidenceArchiveService SHA-256 hashing and gzip archiving."""
    res = evidence_archive_service.archive_evidence(
        evidence_id="ev-test-101",
        marketplace="Meesho",
        source_url="https://www.meesho.com/item/101",
        raw_payload="<html><body><h1>Test Meesho Listing</h1></body></html>",
    )
    assert "archive_id" in res
    assert "response_hash" in res
    assert len(res["response_hash"]) == 64  # SHA-256 length

    meta = evidence_archive_service.get_archive(res["archive_id"])
    assert meta is not None
    assert meta["evidence_id"] == "ev-test-101"


def test_parser_metrics_service():
    """Verify ParserMetricsService extraction telemetry."""
    summary = parser_metrics_service.get_metrics_summary()
    assert "total_dom_nodes_processed" in summary
    assert summary["parsing_success_rate_pct"] > 0


def test_retrieval_confidence_engine():
    """Verify RetrievalConfidenceEngine scoring tiers."""
    c_live = retrieval_confidence_engine.compute_confidence(
        "LIVE_HTTP", http_status=200
    )
    assert c_live["confidence_score"] == 100.0
    assert c_live["confidence_level"] == "HIGH"

    c_fallback = retrieval_confidence_engine.compute_confidence(
        "FALLBACK", http_status=403
    )
    assert c_fallback["confidence_score"] < 50.0


def test_marketplace_retry_engine():
    """Verify MarketplaceRetryEngine rate limits and backoff calculations."""
    allowed = marketplace_retry_engine.check_rate_limit("Amazon")
    assert allowed is True

    delay = marketplace_retry_engine.calculate_backoff_delay(attempt=2)
    assert delay > 1.0


def test_deep_health_rest_apis():
    """Verify deep subsystem health REST API endpoints."""
    endpoints = [
        "/api/v1/health",
        "/api/v1/health/database",
        "/api/v1/health/marketplaces",
        "/api/v1/health/parser",
        "/api/v1/health/scheduler",
        "/api/v1/health/neo4j",
        "/api/v1/health/chromadb",
        "/api/v1/health/storage",
    ]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data or "subsystem" in data


def test_providers_rest_apis():
    """Verify provider health, rate limits, and parser metrics REST APIs."""
    r_health = client.get("/api/v1/providers/health")
    assert r_health.status_code == 200
    assert "providers" in r_health.json()

    r_limits = client.get("/api/v1/providers/rate-limits")
    assert r_limits.status_code == 200
    assert "Amazon" in r_limits.json()

    r_parser = client.get("/api/v1/providers/parser-metrics")
    assert r_parser.status_code == 200
    assert "total_dom_nodes_processed" in r_parser.json()
