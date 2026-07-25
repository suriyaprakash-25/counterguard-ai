from unittest.mock import patch

import pytest

from backend.agents.coordinator import CoordinatorAgent
from backend.agents.specialists import PriceAgent
from backend.schemas.investigation import EvidenceResult
from backend.schemas.llm_models import AIInvestigationResult, PriceAnalysisResult
from backend.schemas.scraping import ParsedListing, ScrapingResult


@pytest.fixture
def mock_state():
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
        "evidence": EvidenceResult(structured_evidence={}),
    }


@patch("backend.services.llm_service.LLMService.generate_structured_response")
def test_price_agent(mock_generate, mock_state):
    mock_result = PriceAnalysisResult(
        anomaly_detected=True, reasoning="Low price", risk_score=80
    )
    mock_generate.return_value = mock_result

    agent = PriceAgent()
    state = agent.run(mock_state)

    assert "price_analysis" in state
    assert state["price_analysis"].anomaly_detected is True
    assert state["price_analysis"].risk_score == 80


@patch("backend.services.llm_service.LLMService.generate_structured_response")
def test_coordinator_agent(mock_generate, mock_state):
    mock_result = AIInvestigationResult(
        summary="Looks fake",
        detailed_reasoning="Price and seller bad",
        suspicious_indicators=["price"],
        confidence_score=90.0,
    )
    mock_generate.return_value = mock_result

    # Pre-populate state
    mock_state["price_analysis"] = PriceAnalysisResult(
        anomaly_detected=True, reasoning="Bad", risk_score=90
    )

    agent = CoordinatorAgent()
    state = agent.run(mock_state)

    assert "coordinator_result" in state
    assert state["coordinator_result"].confidence_score == 90.0
    assert state["coordinator_result"].summary == "Looks fake"
