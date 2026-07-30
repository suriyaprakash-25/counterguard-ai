"""
test_threat_reports.py — Pytest suite for Executive Threat Intelligence Report Generator & REST API
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.schemas.threat_report import ThreatReportGenerateRequest
from backend.services.threat_report_service import threat_report_service

client = TestClient(app)


def test_threat_report_service_generation():
    """Verify synthesis of all 11 required executive sections."""
    req = ThreatReportGenerateRequest(product_name="CMF Buds 2a")
    rpt = threat_report_service.generate_executive_report(req)

    assert rpt.product_name == "CMF Buds 2a"
    assert rpt.threat_level == "CRITICAL"
    assert rpt.threat_score >= 70.0
    assert len(rpt.executive_summary) > 20
    assert len(rpt.fraud_ring_summary) > 20
    assert len(rpt.historical_similarity) > 20
    assert len(rpt.evidence_summary) >= 3
    assert len(rpt.graph_insights) > 20
    assert len(rpt.affected_marketplaces) >= 2
    assert len(rpt.high_risk_sellers) >= 2
    assert len(rpt.recommendations) >= 3
    assert len(rpt.enforcement_actions) >= 2
    assert len(rpt.coordinator_reasoning) > 20


def test_threat_report_api_endpoints():
    """Verify POST /api/v1/intelligence/reports/generate and GET /api/v1/intelligence/reports/{id}."""
    r1 = client.post(
        "/api/v1/intelligence/reports/generate",
        json={"product_name": "Sony WH-1000XM5"},
    )
    assert r1.status_code == 200
    data = r1.json()
    assert data["product_name"] == "Sony WH-1000XM5"
    assert "executive_summary" in data

    report_id = data["report_id"]
    r2 = client.get(f"/api/v1/intelligence/reports/{report_id}")
    assert r2.status_code == 200
    assert r2.json()["report_id"] == report_id
