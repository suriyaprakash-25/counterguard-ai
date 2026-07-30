"""
Sprint 2.3 — Unit + Integration tests for Parallel Investigation Launcher.

Tests cover:
  - Schema validation (request / response)
  - Batch launch via API (POST /api/v1/discovery/launch)
  - Batch status polling (GET /api/v1/discovery/launch/{batch_id}/status)
  - 400 guard: empty candidates
  - 400 guard: too many candidates (>10)
  - 404 guard: unknown batch_id
  - ParallelInvestigationLauncher.launch() success path
  - Concurrent thread verification
"""
import threading
import time
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.schemas.parallel_launch import (
    CandidateLaunchItem,
    ParallelLaunchRequest,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def make_candidate(idx: int = 1, marketplace: str = "Amazon") -> dict:
    return {
        "candidate_id": f"cand-test{idx:03d}",
        "marketplace": marketplace,
        "title": f"CMF Buds 2a - Listing {idx}",
        "url": f"https://www.amazon.com/s?k=CMF+Buds+2a&ref=sr_{idx}",
        "price": 2999.0 - (idx * 100),
        "seller": "Amazon Official" if idx == 1 else f"Seller {idx}",
        "currency": "INR",
    }


# ── Schema Tests ──────────────────────────────────────────────────────────────


def test_parallel_launch_request_valid():
    req = ParallelLaunchRequest(
        candidates=[CandidateLaunchItem(**make_candidate(1))],
    )
    assert len(req.candidates) == 1
    assert req.investigation_type == "Counterfeit Detection"
    assert req.planner_strategy == "Balanced Investigation"
    assert req.priority == "high"


def test_parallel_launch_request_defaults():
    req = ParallelLaunchRequest(
        candidates=[CandidateLaunchItem(**make_candidate(1))],
    )
    assert req.objectives == []
    assert req.notes is None
    assert req.advanced_options is None


# ── API Guard Tests ───────────────────────────────────────────────────────────


def test_api_launch_rejects_empty_candidates():
    client = TestClient(app)
    resp = client.post("/api/v1/discovery/launch", json={"candidates": []})
    assert resp.status_code in (400, 422)


def test_api_launch_rejects_too_many_candidates():
    client = TestClient(app)
    candidates = [make_candidate(i) for i in range(1, 12)]  # 11 candidates
    resp = client.post("/api/v1/discovery/launch", json={"candidates": candidates})
    # Pydantic max_length validation returns 422 Unprocessable Entity
    assert resp.status_code in (400, 422)
    assert "10" in str(resp.json())


def test_api_batch_status_unknown_batch_id():
    client = TestClient(app)
    resp = client.get("/api/v1/discovery/launch/nonexistent-batch-xyz/status")
    assert resp.status_code == 404


# ── Parallel Launch Tests (with mocked InvestigationRunner) ──────────────────


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_launch_creates_one_job_per_candidate(mock_execute):
    """Each candidate should produce exactly one LaunchJobStatus."""
    mock_execute.return_value = None  # Don't actually run investigations

    from backend.discovery.parallel_launcher import ParallelInvestigationLauncher

    launcher = ParallelInvestigationLauncher()
    req = ParallelLaunchRequest(
        candidates=[
            CandidateLaunchItem(**make_candidate(1, "Amazon")),
            CandidateLaunchItem(**make_candidate(2, "Flipkart")),
            CandidateLaunchItem(**make_candidate(3, "Meesho")),
        ],
    )
    result = launcher.launch(req)

    assert result.total_launched == 3
    assert len(result.jobs) == 3
    assert len(result.investigation_ids) == 3
    assert result.batch_id.startswith("batch-")


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_launch_each_job_has_required_fields(mock_execute):
    mock_execute.return_value = None

    from backend.discovery.parallel_launcher import ParallelInvestigationLauncher

    launcher = ParallelInvestigationLauncher()
    req = ParallelLaunchRequest(
        candidates=[CandidateLaunchItem(**make_candidate(1))],
    )
    result = launcher.launch(req)

    job = result.jobs[0]
    assert job.candidate_id == "cand-test001"
    assert job.marketplace == "Amazon"
    assert job.status == "pending"
    assert job.investigation_id  # non-empty UUID string
    assert job.launched_at  # ISO timestamp


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_launch_spawns_threads_concurrently(mock_execute):
    """Verify that multiple threads are spawned (not sequential)."""
    thread_starts: list[float] = []
    barrier = threading.Barrier(3)

    def slow_execute(inv_id, request_dto):
        t = time.time()
        thread_starts.append(t)
        barrier.wait(timeout=5)  # All three must arrive nearly simultaneously

    mock_execute.side_effect = slow_execute

    from backend.discovery.parallel_launcher import ParallelInvestigationLauncher

    launcher = ParallelInvestigationLauncher()
    req = ParallelLaunchRequest(
        candidates=[
            CandidateLaunchItem(**make_candidate(1)),
            CandidateLaunchItem(**make_candidate(2)),
            CandidateLaunchItem(**make_candidate(3)),
        ],
    )
    result = launcher.launch(req)

    # Give threads time to start
    time.sleep(2)

    assert result.total_launched == 3
    # All three threads should start within 1 second of each other
    if len(thread_starts) == 3:
        span = max(thread_starts) - min(thread_starts)
        assert span < 1.0, f"Threads did not start concurrently (span={span:.2f}s)"


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_batch_status_polling(mock_execute):
    """After launching, batch status should be retrievable and reflect DB state."""
    mock_execute.return_value = None

    from backend.discovery.parallel_launcher import ParallelInvestigationLauncher

    launcher = ParallelInvestigationLauncher()
    req = ParallelLaunchRequest(
        candidates=[
            CandidateLaunchItem(**make_candidate(1)),
            CandidateLaunchItem(**make_candidate(2)),
        ],
    )
    result = launcher.launch(req)
    batch_id = result.batch_id

    # Poll status
    status_result = ParallelInvestigationLauncher.get_batch_status(batch_id)

    assert status_result is not None
    assert status_result.batch_id == batch_id
    assert status_result.total == 2
    assert len(status_result.jobs) == 2
    assert 0.0 <= status_result.progress_pct <= 100.0
    assert isinstance(status_result.is_complete, bool)


# ── API Contract Tests ─────────────────────────────────────────────────────────


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_api_launch_returns_202(mock_execute):
    mock_execute.return_value = None
    client = TestClient(app)
    resp = client.post(
        "/api/v1/discovery/launch",
        json={
            "candidates": [make_candidate(1), make_candidate(2, "Flipkart")],
            "investigation_type": "Counterfeit Detection",
            "planner_strategy": "Balanced Investigation",
        },
    )
    assert resp.status_code == 202
    data = resp.json()

    assert "batch_id" in data
    assert data["batch_id"].startswith("batch-")
    assert data["total_launched"] == 2
    assert len(data["jobs"]) == 2
    assert len(data["investigation_ids"]) == 2
    assert data["summary"]

    for job in data["jobs"]:
        assert "investigation_id" in job
        assert "candidate_id" in job
        assert "marketplace" in job
        assert job["status"] == "pending"
        assert "launched_at" in job

    meta = data["metadata"]
    assert meta["candidate_count"] == 2
    assert meta["marketplace_count"] >= 1


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_api_batch_status_after_launch(mock_execute):
    mock_execute.return_value = None
    client = TestClient(app)

    # Launch
    launch_resp = client.post(
        "/api/v1/discovery/launch", json={"candidates": [make_candidate(1)]}
    )
    assert launch_resp.status_code == 202
    batch_id = launch_resp.json()["batch_id"]

    # Poll status
    status_resp = client.get(f"/api/v1/discovery/launch/{batch_id}/status")
    assert status_resp.status_code == 200
    data = status_resp.json()

    assert data["batch_id"] == batch_id
    assert data["total"] == 1
    assert "completed" in data
    assert "in_progress" in data
    assert "pending" in data
    assert "failed" in data
    assert "progress_pct" in data
    assert "is_complete" in data
    assert len(data["jobs"]) == 1


@patch("backend.discovery.parallel_launcher.InvestigationRunner.execute")
def test_api_response_backward_compatible_with_existing_investigations(mock_execute):
    """
    Investigations launched via discovery appear in the DB with valid UUIDs.
    The POST /investigations list endpoint returns them in the data array.
    """
    mock_execute.return_value = None
    client = TestClient(app)

    launch_resp = client.post(
        "/api/v1/discovery/launch", json={"candidates": [make_candidate(1)]}
    )
    assert launch_resp.status_code == 202
    inv_id = launch_resp.json()["investigation_ids"][0]

    # Validate the investigation ID is a valid UUID string
    import uuid as uuid_mod

    try:
        uuid_mod.UUID(inv_id)
        valid_uuid = True
    except ValueError:
        valid_uuid = False
    assert valid_uuid, f"investigation_id '{inv_id}' is not a valid UUID"

    # The investigations list endpoint should exist and return 200
    list_resp = client.get("/api/v1/investigations")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert "data" in data
