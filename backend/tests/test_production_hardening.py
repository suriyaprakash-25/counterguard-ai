"""
test_production_hardening.py — Pytest suite for Production Hardening (Health, Metrics, Config)
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.core.config import settings

client = TestClient(app)


def test_production_config():
    """Verify settings configuration loading."""
    assert settings.APP_NAME == "CounterGuard Intelligence Platform"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.RATE_LIMIT_PER_MINUTE > 0


def test_health_check_endpoint():
    """Verify GET /api/v1/health returns HEALTHY status and service status."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "services" in data
    assert data["services"]["sqlite_database"] == "CONNECTED"
    assert data["services"]["neo4j_threat_graph"] == "ONLINE"
    assert "resources" in data


def test_metrics_endpoint():
    """Verify GET /api/v1/metrics returns Prometheus plaintext metrics."""
    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    assert "counterguard_uptime_seconds" in res.text
