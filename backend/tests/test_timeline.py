import pytest
from backend.utils.timeline import log_event
from backend.state import InvestigationState

def test_log_event():
    state: InvestigationState = {
        "listing_id": "L-1",
        "listing_data": {},
        "evidence_timeline": [],
        "agent_findings": {},
        "confidence_score": 50.0,
        "cross_query_count": 0,
        "status": "scanning",
        "legal_notice_draft": None
    }
    
    log_event(state, "test_agent", "test_action", "detail", 15.0)
    
    assert len(state["evidence_timeline"]) == 1
    assert state["evidence_timeline"][0]["agent"] == "test_agent"
    assert state["evidence_timeline"][0]["confidence_delta"] == 15.0
    assert state["confidence_score"] == 65.0

def test_log_event_confidence_caps():
    state: InvestigationState = {
        "listing_id": "L-1",
        "listing_data": {},
        "evidence_timeline": [],
        "agent_findings": {},
        "confidence_score": 90.0,
        "cross_query_count": 0,
        "status": "scanning",
        "legal_notice_draft": None
    }
    
    log_event(state, "test_agent", "action", "detail", 20.0)
    assert state["confidence_score"] == 100.0  # capped at 100
    
    log_event(state, "test_agent", "action", "detail", -150.0)
    assert state["confidence_score"] == 0.0  # capped at 0
