import pytest
from backend.agents.scout import ScoutAgent
from backend.state import InvestigationState

def test_scout_run_success():
    agent = ScoutAgent()
    initial_state: InvestigationState = {
        "listing_id": "L-1",
        "listing_data": {"test_key": "val"},
        "evidence_timeline": [],
        "agent_findings": {},
        "confidence_score": 0.0,
        "cross_query_count": 0,
        "status": "scanning",
        "legal_notice_draft": None
    }
    
    result = agent.run(initial_state)
    assert "scout" in result["agent_findings"]
    assert result["agent_findings"]["scout"]["processed"] is True
    assert "test_key" in result["agent_findings"]["scout"]["data_keys"]
    
    assert len(result["evidence_timeline"]) == 1
    assert result["evidence_timeline"][0]["action"] == "discovered_listing"

def test_scout_run_missing_listing_id():
    agent = ScoutAgent()
    initial_state: InvestigationState = {
        "listing_id": "",
        "listing_data": {},
        "evidence_timeline": [],
        "agent_findings": {},
        "confidence_score": 0.0,
        "cross_query_count": 0,
        "status": "scanning",
        "legal_notice_draft": None
    }
    with pytest.raises(ValueError, match="listing_id is required"):
        agent.run(initial_state)
