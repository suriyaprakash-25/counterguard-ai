"""
Sprint 2.5 — Unit and API integration tests for Product Intelligence Report.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.schemas.product_report import (
    ProductIntelligenceReportRequest,
)


def test_product_report_request_validation():
    req = ProductIntelligenceReportRequest(
        investigation_ids=["inv-001", "inv-002"],
        product_name="CMF Buds 2a",
    )
    assert len(req.investigation_ids) == 2
    assert req.product_name == "CMF Buds 2a"


def test_api_report_rejects_empty_ids():
    client = TestClient(app)
    resp = client.post("/api/v1/discovery/report", json={"investigation_ids": []})
    assert resp.status_code in (400, 422)


def test_product_report_service_synthesis():
    from backend.discovery.product_report_service import ProductReportService

    inv1 = MagicMock()
    inv1.id = "inv-test-101"
    inv1.listing_url = "https://amazon.in/dp/B001"
    inv1.marketplace = "Amazon"
    inv1.status = "completed"
    inv1.risk_score = 20.0
    inv1.verdict = "LOW"
    inv1.overall_confidence = 0.9
    inv1.evidence_list = []
    inv1.updated_at = None
    inv1.context = {
        "product_title": "CMF Buds 2a Original",
        "seller_name": "Official Store",
        "price": 2999,
    }

    inv2 = MagicMock()
    inv2.id = "inv-test-102"
    inv2.listing_url = "https://meesho.com/s/123"
    inv2.marketplace = "Meesho"
    inv2.status = "completed"
    inv2.risk_score = 85.0
    inv2.verdict = "CRITICAL"
    inv2.overall_confidence = 0.85
    inv2.evidence_list = []
    inv2.updated_at = None
    inv2.context = {
        "product_title": "CMF Buds 2a Master Copy",
        "seller_name": "FakeSeller",
        "price": 299,
    }

    with patch("backend.discovery.product_report_service.get_session_maker") as mock_sm:
        mock_db = MagicMock()
        mock_sm.return_value = lambda: mock_db
        mock_repo = MagicMock()
        mock_db.query.return_value = mock_repo

        # mock repo get_by_id
        def get_by_id_side_effect(id_str):
            if id_str == "inv-test-101":
                return inv1
            if id_str == "inv-test-102":
                return inv2
            return None

        with patch(
            "backend.discovery.product_report_service.InvestigationRepository"
        ) as mock_repo_cls:
            mock_instance = MagicMock()
            mock_instance.get_by_id.side_effect = get_by_id_side_effect
            mock_repo_cls.return_value = mock_instance

            service = ProductReportService()
            req = ProductIntelligenceReportRequest(
                investigation_ids=["inv-test-101", "inv-test-102"]
            )
            report = service.generate_report(req)

            assert report.total_listings == 2
            assert report.safe_listings == 1
            assert report.suspicious_listings == 1
            assert report.overall_product_risk == 52.5
            assert report.overall_risk_level == "MEDIUM"
            assert report.highest_risk_marketplace == "Meesho"
            assert report.recommended_seller == "Official Store"
            assert report.marketplace_distribution == {"Amazon": 1, "Meesho": 1}
            assert len(report.investigations) == 2


def test_api_report_endpoint():
    client = TestClient(app)
    resp = client.post(
        "/api/v1/discovery/report",
        json={"investigation_ids": ["nonexistent-id-001"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "report_id" in data
    assert "total_listings" in data
    assert "overall_product_risk" in data
    assert "coordinator_summary" in data
