"""
test_closed_loop_intelligence.py — Pytest suite for Closed-Loop Intelligence Engine
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.schemas.closed_loop import ClosedLoopTriggerRequest
from backend.services.closed_loop_intelligence_engine import (
    closed_loop_intelligence_engine,
)

client = TestClient(app)


def test_closed_loop_engine_execution():
    """Verify 8-stage closed-loop pipeline execution."""
    req = ClosedLoopTriggerRequest(case_id="INV-8901", product_name="CMF Buds 2a")
    res = closed_loop_intelligence_engine.trigger_closed_loop_pipeline(req)
    assert res.status == "SUCCESS"
    assert len(res.stages) == 8
    assert res.stages[0].stage_name == "Update Threat Graph"
    assert res.stages[7].stage_name == "Trigger Multi-Channel Alerts"
    assert res.total_duration_ms > 0
    assert res.report_id.startswith("rpt-")


def test_closed_loop_api_endpoints():
    """Verify POST /api/v1/intelligence/closed-loop/trigger and GET /api/v1/intelligence/closed-loop/telemetry."""
    r1 = client.post(
        "/api/v1/intelligence/closed-loop/trigger",
        json={"case_id": "INV-8901", "product_name": "CMF Buds 2a"},
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "SUCCESS"
    assert len(r1.json()["stages"]) == 8

    r2 = client.get("/api/v1/intelligence/closed-loop/telemetry?case_id=INV-8901")
    assert r2.status_code == 200
    assert r2.json()["case_id"] == "INV-8901"
