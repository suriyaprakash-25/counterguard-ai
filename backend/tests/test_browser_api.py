"""
test_browser_api.py — Unit tests for Chrome Extension Browser API (POST /api/v1/browser/analyze)
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_browser_analyze_product_card_success():
    payload = {
        "title": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
        "seller": "Appario Retail Private Ltd",
        "price": 29990.0,
        "currency": "INR",
        "url": "https://www.amazon.in/dp/B0CX237A12",
        "image": "https://images-na.ssl-images-amazon.com/images/I/61+jNfc77EL._AC_SL1500_.jpg",
        "rating": 4.5,
        "review_count": 1245,
        "availability": "In Stock",
        "brand": "Sony",
        "marketplace": "Amazon",
        "confidence_score": 100.0
    }

    response = client.post("/api/v1/browser/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "risk_score" in data
    assert "threat_level" in data
    assert "seller_trust" in data
    assert "recommendation" in data
    assert "investigation_id" in data
    assert "evidence_id" in data
    assert isinstance(data["findings"], list)
    assert data["investigation_id"].startswith("inv-")
    assert data["evidence_id"].startswith("ev-")


def test_browser_analyze_counterfeit_risk_flagging():
    payload = {
        "title": "Super Replica Copy Sony Headphones Cheap",
        "seller": "Unverified Seller 999",
        "price": 299.0,
        "currency": "INR",
        "url": "https://www.meesho.com/p/1a2b3c",
        "rating": 2.1,
        "availability": "In Stock",
        "marketplace": "Meesho",
        "confidence_score": 90.0
    }

    response = client.post("/api/v1/browser/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["threat_level"] in ["HIGH", "CRITICAL"]
    assert data["risk_score"] >= 50.0
    assert data["seller_trust"] < 60.0
    assert len(data["findings"]) > 0
