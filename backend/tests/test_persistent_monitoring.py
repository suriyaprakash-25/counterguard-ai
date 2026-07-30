"""
test_persistent_monitoring.py — Pytest suite for Autonomous SQLite-Persisted Continuous Monitoring Platform
Verifies database schema creation, repositories, APScheduler lifecycle, Watchlist integration, and execution history persistence.
"""
import time

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.database.engine import get_engine
from backend.models.monitoring import (
    Base,
    MonitoringJobModel,
)
from backend.repositories.monitoring_repository import (
    monitoring_event_repo,
    monitoring_history_repo,
    monitoring_job_repo,
)
from backend.services.monitoring_orchestrator import monitoring_orchestrator
from backend.services.watchlist_manager import watchlist_manager

client = TestClient(app)


def setup_module(module):
    """Initialize SQLite tables before test execution."""
    Base.metadata.create_all(bind=get_engine())


def test_monitoring_database_tables_exist():
    """Verify SQLite database schema creation for monitoring models."""
    engine = get_engine()
    tables = engine.dialect.get_table_names(engine.connect())
    assert "monitoring_jobs" in tables
    assert "monitoring_history" in tables
    assert "monitoring_events" in tables
    assert "watchlists" in tables


def test_monitoring_repository_crud():
    """Verify MonitoringJobRepository CRUD operations with SQLite."""
    test_id = f"test-job-{int(time.time())}"
    job = MonitoringJobModel(
        id=test_id,
        name="Test Watchlist SKU",
        query="Test SKU",
        marketplaces='["Amazon"]',
        interval="15m",
        status="ACTIVE",
        total_scans=1,
    )
    saved = monitoring_job_repo.save(job)
    assert saved.id == test_id

    fetched = monitoring_job_repo.get_by_id(test_id)
    assert fetched is not None
    assert fetched.name == "Test Watchlist SKU"

    # Cleanup
    monitoring_job_repo.delete(test_id)


def test_watchlist_manager_persists_to_sqlite_and_creates_job():
    """Verify WatchlistManager creates persistent SQLite watchlists and linked monitoring jobs."""
    from backend.schemas.watchlist import WatchlistCreateRequest

    req = WatchlistCreateRequest(
        category="PRODUCT",
        value="Sony WH-1000XM5 OEM",
        name="Sony XM5 Watchlist Test",
    )
    dto = watchlist_manager.create_watchlist_item(req)
    assert dto.id.startswith("wl-")

    # Check job was created in SQLite
    job_id = f"job-{dto.id}"
    job = monitoring_job_repo.get_by_id(job_id)
    assert job is not None
    assert job.name == "Sony XM5 Watchlist Test Watchlist"
    assert job.status == "ACTIVE"

    # Clean up
    watchlist_manager.delete_watchlist_item(dto.id)


def test_monitoring_orchestrator_execution_persists_history():
    """Verify run_monitoring_cycle executes pipeline and persists history/events to SQLite."""
    import asyncio

    res = asyncio.run(monitoring_orchestrator.run_monitoring_cycle("job-cmf-buds"))
    assert "message" in res
    assert "duration_ms" in res["execution"].__dict__ or hasattr(
        res["execution"], "duration_ms"
    )

    # Verify history was saved to SQLite
    history = monitoring_history_repo.get_history(limit=5)
    assert len(history) > 0
    latest_exec = history[0]
    assert latest_exec.job_id == "job-cmf-buds"
    assert latest_exec.status == "SUCCESS"
    assert latest_exec.duration_ms > 0

    # Verify events were saved to SQLite
    events = monitoring_event_repo.get_recent_events(limit=5)
    assert len(events) > 0


def test_apscheduler_lifecycle_and_endpoints():
    """Verify GET /api/v1/monitor/jobs and POST /api/v1/monitor/run API responses."""
    resp_get = client.get("/api/v1/monitor/jobs")
    assert resp_get.status_code == 200
    data = resp_get.json()
    assert "active_jobs" in data
    assert "completed_scans" in data
    assert "jobs" in data

    resp_post = client.post("/api/v1/monitor/run?job_id=job-cmf-buds")
    assert resp_post.status_code == 200
    post_data = resp_post.json()
    assert "report_id" in post_data
    assert "execution" in post_data
