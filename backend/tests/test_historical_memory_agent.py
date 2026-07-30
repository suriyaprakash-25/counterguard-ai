"""
test_historical_memory_agent.py — Pytest suite for Organizational Memory Agent & REST API
"""
from fastapi.testclient import TestClient

from backend.agents.historical_memory_agent import historical_memory_agent
from backend.api.main import app

client = TestClient(app)


def test_historical_memory_agent_search():
    """Verify vector search across historical precedents."""
    resp = historical_memory_agent.search_similar_investigations("CMF Buds")
    assert resp.total_matches >= 1
    assert resp.matches[0].similarity_pct > 70.0
    assert "Precedent match" in resp.recommendation


def test_memory_api_endpoints():
    """Verify GET /api/v1/memory/similar-investigations, sellers, products, evidence."""
    r1 = client.get("/api/v1/memory/similar-investigations?query=CMF%20Buds")
    assert r1.status_code == 200
    assert "matches" in r1.json()

    r2 = client.get("/api/v1/memory/similar-sellers?seller=Radha")
    assert r2.status_code == 200
    assert "matches" in r2.json()

    r3 = client.get("/api/v1/memory/similar-products?product=Sony")
    assert r3.status_code == 200
    assert "matches" in r3.json()

    r4 = client.get("/api/v1/memory/similar-evidence?query=Anomaly")
    assert r4.status_code == 200
    assert "matches" in r4.json()
