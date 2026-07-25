from unittest.mock import patch

import pytest

from backend.agents.planner import PlanningAgent
from backend.schemas.investigation import AnalyzerResult, EvidenceResult
from backend.schemas.llm_models import PlanningResult
from backend.schemas.scraping import ParsedListing, ScrapingResult


@pytest.fixture
def mock_planner_state():
    return {
        "scraping_result": ScrapingResult(
            success=True,
            listing=ParsedListing(
                url="http://test.com",
                marketplace="Amazon",
                title="Fake Watch",
                price=10.0,
            ),
        ),
        "analysis": AnalyzerResult(
            brand="GenericBrand",
            title="Fake Watch",
            price=10.0,
            seller_rating=2.5,
            marketplace="Amazon",
            risk_signals=["very_low_price"],
        ),
        "evidence": EvidenceResult(structured_evidence={}),
    }


@patch("backend.services.llm_service.LLMService.generate_structured_response")
def test_planning_agent_success(mock_generate, mock_planner_state):
    mock_result = PlanningResult(
        selected_specialists=["PriceAgent", "SellerAgent"],
        priority="High",
        execution_strategy="Check pricing heavily.",
        rationale="Low price flag triggered.",
    )
    mock_generate.return_value = mock_result

    agent = PlanningAgent()
    state = agent.run(mock_planner_state)

    assert "planning_result" in state
    assert "PriceAgent" in state["planning_result"].selected_specialists
    assert state["planning_result"].priority == "High"


@patch("backend.services.llm_service.LLMService.generate_structured_response")
def test_planning_agent_fallback(mock_generate, mock_planner_state):
    from backend.services.llm_service import LLMServiceError

    mock_generate.side_effect = LLMServiceError("API down")

    agent = PlanningAgent()
    state = agent.run(mock_planner_state)

    # Should trigger fallback which runs all specialists
    assert "planning_result" in state
    assert len(state["planning_result"].selected_specialists) == 4
    assert "Fallback" in state["planning_result"].execution_strategy
