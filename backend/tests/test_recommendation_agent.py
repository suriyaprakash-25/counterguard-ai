"""
test_recommendation_agent.py — Pytest suite for AI Prescriptive Recommendation Agent
"""
from fastapi.testclient import TestClient

from backend.agents.recommendation_agent import recommendation_agent
from backend.api.main import app

client = TestClient(app)


def test_recommendation_agent_generation():
    """Verify deterministic generation of prescriptive action recommendations."""
    res = recommendation_agent.generate_prescriptive_recommendations("CMF Buds 2a")
    assert res.target_product == "CMF Buds 2a"
    assert res.overall_confidence > 80.0
    assert len(res.recommendations) >= 4

    rec = res.recommendations[0]
    assert rec.action_type in [
        "INVESTIGATE_IMMEDIATELY",
        "ISSUE_TAKEDOWN",
        "ESCALATE_LEGAL",
        "MERGE_CASE",
    ]
    assert rec.confidence >= 80.0
    assert len(rec.reasoning) >= 2
    assert len(rec.supporting_evidence) >= 1
    assert len(rec.supporting_graph_entities) >= 1


def test_recommendation_execution():
    """Verify one-click recommendation execution."""
    exec_res = recommendation_agent.execute_recommendation(
        type(
            "Req",
            (),
            {
                "recommendation_id": "rec-inv-001",
                "action_type": "INVESTIGATE_IMMEDIATELY",
                "notes": "Test execution",
            },
        )()
    )
    assert exec_res["status"] == "EXECUTED"
    assert exec_res["case_created"] is True
    assert exec_res["case_id"] == "INV-9099"


def test_recommendations_api_endpoints():
    """Verify GET /api/v1/recommendations/prescriptive and POST /api/v1/recommendations/execute."""
    r1 = client.get("/api/v1/recommendations/prescriptive?target_query=Sony%20XM5")
    assert r1.status_code == 200
    assert "recommendations" in r1.json()

    r2 = client.post(
        "/api/v1/recommendations/execute",
        json={"recommendation_id": "rec-td-002", "action_type": "ISSUE_TAKEDOWN"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "EXECUTED"
    assert r2.json()["enforcement_dispatched"] is True
