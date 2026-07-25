from unittest.mock import patch

import pytest

from backend.agents.investigation_agent import InvestigationAgent
from backend.schemas.investigation import AnalyzerResult, EvidenceResult
from backend.schemas.llm_models import AIInvestigationResult
from backend.schemas.scraping import ParsedListing, ScrapingResult
from backend.services.llm_service import LLMServiceError


@pytest.fixture
def sample_payloads():
    scraping_result = ScrapingResult(
        success=True,
        listing=ParsedListing(
            url="https://test.com",
            marketplace="test",
            title="Fake Test Item",
            price=10.0,
        ),
    )
    analysis = AnalyzerResult(
        brand="Unknown",
        title="Fake Test Item",
        price=10.0,
        seller_rating=0.0,
        marketplace="test",
        risk_signals=["very_low_price"],
    )
    evidence = EvidenceResult(
        structured_evidence={"price": {"status": "Suspicious", "reason": "Too low"}}
    )
    return scraping_result, analysis, evidence


def test_investigation_agent_success(sample_payloads):
    scraping_result, analysis, evidence = sample_payloads

    agent = InvestigationAgent()

    mock_llm_result = AIInvestigationResult(
        summary="Clear fake.",
        detailed_reasoning="The price is too low.",
        suspicious_indicators=["very_low_price"],
        confidence_score=95.0,
    )

    with patch.object(
        agent.llm_service, "generate_investigation_result", return_value=mock_llm_result
    ):
        result = agent.investigate(scraping_result, analysis, evidence)

        assert result.summary == "Clear fake."
        assert result.confidence_score == 95.0
        assert "very_low_price" in result.suspicious_indicators


def test_investigation_agent_fallback_on_error(sample_payloads):
    scraping_result, analysis, evidence = sample_payloads

    agent = InvestigationAgent()

    with patch.object(
        agent.llm_service,
        "generate_investigation_result",
        side_effect=LLMServiceError("API down"),
    ):
        result = agent.investigate(scraping_result, analysis, evidence)

        # Should return fallback instead of blowing up the orchestrator
        assert result.confidence_score == 50.0
        assert "unavailable" in result.summary.lower()
