import pytest
from unittest.mock import MagicMock, patch
from backend.services.investigation_engine import InvestigationEngine
from backend.exceptions import InvestigationExecutionError
from backend.state import InvestigationState

@patch("backend.services.investigation_engine.get_compiled_graph")
def test_engine_run_success(mock_get_graph):
    mock_app = MagicMock()
    mock_state: InvestigationState = {
        "listing_id": "L-1",
        "listing_data": {},
        "evidence_timeline": [],
        "agent_findings": {},
        "confidence_score": 0.0,
        "cross_query_count": 0,
        "status": "scanning",
        "legal_notice_draft": None
    }
    mock_app.invoke.return_value = mock_state
    mock_get_graph.return_value = mock_app
    
    engine = InvestigationEngine()
    result = engine.run("L-1")
    
    assert result == mock_state
    mock_app.invoke.assert_called_once()

@patch("backend.services.investigation_engine.get_compiled_graph")
def test_engine_run_error(mock_get_graph):
    mock_app = MagicMock()
    mock_app.invoke.side_effect = Exception("Test error")
    mock_get_graph.return_value = mock_app
    
    engine = InvestigationEngine()
    with pytest.raises(InvestigationExecutionError):
        engine.run("L-1")
