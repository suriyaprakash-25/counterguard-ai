"""
test_monitoring_platform.py — Pytest suite for Proactive Continuous Monitoring Platform
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.services.monitoring_orchestrator import monitoring_orchestrator
from backend.services.monitoring_scheduler import monitoring_scheduler

client = TestClient(app)


def test_monitoring_scheduler_controls():
    """Verify job intervals, pause, resume, and manual trigger controls."""
    jobs = monitoring_scheduler.get_all_jobs()
    assert len(jobs) >= 4

    p_job = monitoring_scheduler.pause_job("job-cmf-buds")
    assert p_job.status == "PAUSED"

    r_job = monitoring_scheduler.resume_job("job-cmf-buds")
    assert r_job.status == "ACTIVE"


def test_monitoring_orchestrator_pipeline():
    """Verify execution of continuous monitoring cycle."""
    import asyncio

    res = asyncio.run(monitoring_orchestrator.run_monitoring_cycle("job-cmf-buds"))
    assert "job" in res
    assert "execution" in res
    assert "report_id" in res
    assert res["execution"].status == "SUCCESS"


def test_monitoring_api_endpoints():
    """Verify REST API endpoints for monitoring jobs, history, run, pause, resume."""
    r1 = client.get("/api/v1/monitor/jobs")
    assert r1.status_code == 200
    assert r1.json()["active_jobs"] >= 1

    r2 = client.get("/api/v1/monitor/history")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)

    r3 = client.post("/api/v1/monitor/run?job_id=job-sony-xm5")
    assert r3.status_code == 200
    assert "execution" in r3.json()

    r4 = client.post("/api/v1/monitor/pause?job_id=job-sony-xm5")
    assert r4.status_code == 200
    assert r4.json()["status"] == "PAUSED"

    r5 = client.post("/api/v1/monitor/resume?job_id=job-sony-xm5")
    assert r5.status_code == 200
    assert r5.json()["status"] == "ACTIVE"
