import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.discovery.router import MarketplaceRouter
from backend.discovery.service import DiscoveryService
from backend.schemas.discovery import DiscoverySearchRequest, ListingCandidate


def test_query_normalization():
    assert DiscoveryService.normalize_query("  CMF   Buds   2a  ") == "CMF Buds 2a"
    assert DiscoveryService.normalize_query("Nike   Air   Max") == "Nike Air Max"
    assert DiscoveryService.normalize_query("") == ""


@pytest.mark.asyncio
async def test_marketplace_router_registration_and_search():
    router = MarketplaceRouter()
    supported = router.get_supported_marketplaces()

    assert "Amazon" in supported
    assert "Flipkart" in supported
    assert "Meesho" in supported
    assert "TradeIndia" in supported
    assert "AJIO" in supported
    assert "Myntra" in supported
    assert len(supported) == 6

    candidates = await router.search(query="CMF Buds 2a", limit_per_marketplace=2)
    assert len(candidates) > 0
    assert any(c.marketplace == "Amazon" for c in candidates)
    assert any(c.marketplace == "Flipkart" for c in candidates)

    for c in candidates:
        assert isinstance(c, ListingCandidate)
        assert c.id is not None
        assert c.title != ""
        assert c.url.startswith("http")
        assert c.confidence >= 0.0 and c.confidence <= 1.0


@pytest.mark.asyncio
async def test_discovery_service_end_to_end():
    service = DiscoveryService()
    req = DiscoverySearchRequest(
        query="Sony WH-1000XM5", marketplaces=["Amazon", "Flipkart"]
    )
    res = await service.discover_products(req)

    assert res.query == "Sony WH-1000XM5"
    assert res.normalized_query == "Sony WH-1000XM5"
    assert "Amazon" in res.marketplaces_searched
    assert "Flipkart" in res.marketplaces_searched
    assert len(res.candidates) > 0
    assert res.metadata["candidate_count"] == len(res.candidates)


def test_discovery_api_endpoints():
    client = TestClient(app)

    # 1. Test GET /api/v1/discovery/marketplaces
    resp_marketplaces = client.get("/api/v1/discovery/marketplaces")
    assert resp_marketplaces.status_code == 200
    m_data = resp_marketplaces.json()
    assert m_data["count"] == 6
    assert "Amazon" in m_data["supported_marketplaces"]

    # 2. Test POST /api/v1/discovery/search
    resp_search = client.post(
        "/api/v1/discovery/search",
        json={"query": "CMF Buds 2a", "limit_per_marketplace": 2},
    )
    assert resp_search.status_code == 200
    s_data = resp_search.json()
    assert s_data["query"] == "CMF Buds 2a"
    assert s_data["normalized_query"] == "CMF Buds 2a"
    assert len(s_data["candidates"]) >= 6
    assert s_data["candidates"][0]["id"] is not None
    assert s_data["candidates"][0]["title"] is not None

    # 3. Test empty query validation
    resp_bad = client.post("/api/v1/discovery/search", json={"query": "   "})
    assert resp_bad.status_code == 400
