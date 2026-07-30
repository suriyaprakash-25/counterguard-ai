"""
test_threat_scoring_engine.py — Pytest suite for Hierarchical Threat Scoring Engine
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.services.threat_scoring_engine import threat_scoring_engine

client = TestClient(app)


def test_threat_scoring_engine_computation():
    """Verify 8 entity hierarchy scores calculation."""
    res = threat_scoring_engine.compute_hierarchical_scores("prod-cmf-buds")
    assert res.overall_organization_risk > 50.0
    assert len(res.hierarchy_scores) == 8

    # Verify all 8 entity levels exist
    levels = [
        "Listing",
        "Seller",
        "Product",
        "Marketplace",
        "Fraud Ring",
        "Evidence",
        "Investigation",
        "Organization",
    ]
    for lvl in levels:
        assert lvl in res.hierarchy_scores
        score_item = res.hierarchy_scores[lvl]
        assert score_item.threat_score >= 0.0
        assert len(score_item.reasoning) > 0


def test_scoring_api_endpoints():
    """Verify GET /api/v1/scoring/hierarchical and /explain/{entity_id}."""
    r1 = client.get("/api/v1/scoring/hierarchical?entity_id=prod-cmf-buds")
    assert r1.status_code == 200
    data = r1.json()
    assert "hierarchy_scores" in data

    r2 = client.get("/api/v1/scoring/explain/seller-radha")
    assert r2.status_code == 200
    assert "factor_contributions" in r2.json()
    assert "reasoning" in r2.json()
