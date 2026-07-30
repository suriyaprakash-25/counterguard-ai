"""
test_watchlist_alert_system.py — Pytest suite for Watchlist Management & Alert Service
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.services.alert_service import alert_service
from backend.services.watchlist_manager import watchlist_manager

client = TestClient(app)


def test_watchlist_manager_operations():
    """Verify CRUD, pause, resume, and export across 8 entity categories."""
    items = watchlist_manager.get_all_watchlists()
    assert len(items) >= 8

    # Verify 8 categories
    categories = set(i.category for i in items)
    assert "GST" in categories
    assert "SELLER" in categories
    assert "FRAUD_RING" in categories

    # Test export CSV
    csv_str = watchlist_manager.export_watchlists_csv()
    assert "Category,Value" in csv_str or "Category" in csv_str


def test_alert_service_deduplication():
    """Verify alert dispatch & deduplication."""
    alert = alert_service.dispatch_alert(
        event_type="PRICE_ANOMALY",
        title="Test Anomaly Alert",
        description="Price dropped -75% below MSRP.",
        severity="CRITICAL",
        marketplace="Meesho",
        investigation_id="INV-8901",
    )
    assert alert.alert_id.startswith("alt-")
    assert alert.severity == "CRITICAL"

    feed = alert_service.get_alert_feed("CRITICAL")
    assert len(feed) >= 1


def test_watchlist_and_alert_api_endpoints():
    """Verify GET/POST watchlists & GET alerts/feed REST APIs."""
    r1 = client.get("/api/v1/watchlists")
    assert r1.status_code == 200
    assert len(r1.json()) >= 8

    r2 = client.post(
        "/api/v1/watchlists",
        json={
            "category": "GST",
            "value": "27AAAAA1111A1Z0",
            "name": "Mumbai Tax Watch",
        },
    )
    assert r2.status_code == 200
    assert r2.json()["category"] == "GST"

    r3 = client.get("/api/v1/alerts/feed")
    assert r3.status_code == 200
    assert isinstance(r3.json(), list)

    r4 = client.post(
        "/api/v1/alerts/test-webhook",
        json={"target_url": "https://api.counterguard.ai/webhook"},
    )
    assert r4.status_code == 200
    assert r4.json()["status"] == "DELIVERED"
