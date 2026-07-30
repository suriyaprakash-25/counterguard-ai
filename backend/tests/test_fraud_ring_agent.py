"""
test_fraud_ring_agent.py — Pytest suite for Fraud Ring Intelligence Agent & API
"""
from fastapi.testclient import TestClient

from backend.agents.fraud_ring_agent import fraud_ring_agent
from backend.api.main import app

client = TestClient(app)


def test_fraud_ring_agent_analysis():
    """Verify FraudRingAgent graph clustering and detection rules."""
    result = fraud_ring_agent.analyze_graph_for_fraud_rings()
    assert result.total_rings >= 2
    assert result.critical_count >= 1

    first_ring = result.rings[0]
    assert first_ring.threat_level == "CRITICAL"
    assert first_ring.member_count >= 2
    assert len(first_ring.shared_identifiers) > 0
    assert len(first_ring.supporting_evidence) > 0


def test_fraud_ring_api_endpoints():
    """Verify GET /api/v1/threat/rings and sub-endpoints."""
    resp = client.get("/api/v1/threat/rings")
    assert resp.status_code == 200
    data = resp.json()
    assert "rings" in data
    assert data["total_rings"] >= 2

    # Detail endpoint
    ring_id = data["rings"][0]["ring_id"]
    resp_detail = client.get(f"/api/v1/threat/rings/{ring_id}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["ring_id"] == ring_id

    # Members endpoint
    resp_members = client.get(f"/api/v1/threat/rings/{ring_id}/members")
    assert resp_members.status_code == 200
    assert isinstance(resp_members.json(), list)

    # Evidence endpoint
    resp_evidence = client.get(f"/api/v1/threat/rings/{ring_id}/evidence")
    assert resp_evidence.status_code == 200
    assert isinstance(resp_evidence.json(), list)
