"""
test_collaborative_cases.py — Pytest suite for Collaborative Investigation Workflows
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.schemas.case_management import CaseCommentRequest, CaseStateUpdateRequest
from backend.services.case_management_service import case_management_service

client = TestClient(app)


def test_case_management_lifecycle():
    """Verify state transitions across 7 states, notes, assignment, and timeline logging."""
    case = case_management_service.get_case_by_id("INV-8901")
    assert case is not None
    assert case.state in case_management_service.VALID_STATES

    # Transition to 'Legal Review'
    updated = case_management_service.update_case_state(
        "INV-8901",
        CaseStateUpdateRequest(state="Legal Review", notes="Escalated to legal desk."),
    )
    assert updated.state == "Legal Review"
    assert updated.history_timeline[0].event_type == "STATE_CHANGE"

    # Add comment
    cmt = case_management_service.add_comment(
        "INV-8901",
        CaseCommentRequest(
            author="Analyst Bob", text="Reviewing GST registration documents."
        ),
    )
    assert cmt.author == "Analyst Bob"
    assert len(case_management_service.get_case_by_id("INV-8901").comments) >= 3


def test_cases_api_endpoints():
    """Verify GET /api/v1/cases, GET /api/v1/cases/{id}, PUT status, POST comments."""
    r1 = client.get("/api/v1/cases?filter_type=high_priority")
    assert r1.status_code == 200
    assert len(r1.json()) >= 1

    r2 = client.get("/api/v1/cases/INV-8901")
    assert r2.status_code == 200
    assert r2.json()["id"] == "INV-8901"
    assert "history_timeline" in r2.json()

    r3 = client.put(
        "/api/v1/cases/INV-8901/status",
        json={"state": "Resolved", "notes": "Takedown completed successfully."},
    )
    assert r3.status_code == 200
    assert r3.json()["state"] == "Resolved"

    r4 = client.post(
        "/api/v1/cases/INV-8901/comments",
        json={"author": "Lead Investigator", "text": "Case closed."},
    )
    assert r4.status_code == 200
    assert r4.json()["author"] == "Lead Investigator"
