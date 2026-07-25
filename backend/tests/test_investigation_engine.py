from unittest.mock import MagicMock, patch

from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.reporter import ReportGenerator
from backend.schemas.investigation import InvestigationRequest
from backend.schemas.scraping import ParsedListing, ScrapingResult
from backend.services.investigation_service import InvestigationService


def get_mock_scraping_result():
    return ScrapingResult(
        success=True,
        listing=ParsedListing(
            brand="GenericBrand",
            title="Suspicious Product from Amazon",
            price=5.0,  # very_low_price
            seller_rating=2.5,  # poor_seller_rating
            seller_name="Unknown Seller",  # missing_seller
            warranty_info=None,  # no_warranty
            images_count=1,  # few_images
            marketplace="Amazon",
        ),
    )


def test_analyzer():
    analyzer = AnalyzerAgent()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    result = analyzer.analyze(request, get_mock_scraping_result())
    assert result.brand == "GenericBrand"
    assert result.marketplace == "Amazon"
    assert result.price == 5.0
    assert result.seller_rating == 2.5
    assert "very_low_price" in result.risk_signals


def test_collector():
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    analysis = analyzer.analyze(request, get_mock_scraping_result())
    evidence = collector.collect(analysis)
    se = evidence.structured_evidence
    assert se["price"]["status"] == "Suspicious"
    assert se["seller"]["status"] == "Missing"
    assert se["warranty"]["status"] == "Missing"
    assert se["images"]["status"] == "Poor"


def test_assessor():
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    assessor = RiskAssessor()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    analysis = analyzer.analyze(request, get_mock_scraping_result())
    evidence = collector.collect(analysis)
    risk = assessor.assess(analysis, evidence)
    # price_anomaly (40) + rating < 3 (25) + missing warranty (10) + poor listing (10) + brand formatting (15) = 100
    assert risk.risk_score == 100
    assert risk.risk_level == "HIGH"


def test_reporter():
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    assessor = RiskAssessor()
    reporter = ReportGenerator()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    analysis = analyzer.analyze(request, get_mock_scraping_result())
    evidence = collector.collect(analysis)
    risk = assessor.assess(analysis, evidence)
    report = reporter.generate(analysis, evidence, risk)

    assert report.risk_score == 100
    assert report.risk_level == "HIGH"
    assert any("Price Anomaly" in f for f in report.findings)
    assert report.recommendation == "Immediate takedown recommended."


def get_mock_structured_response(system_prompt, user_prompt, response_model):
    from backend.schemas.llm_models import (
        AIInvestigationResult,
        BrandAnalysisResult,
        PriceAnalysisResult,
        ReviewAnalysisResult,
        SellerAnalysisResult,
    )

    if response_model == PriceAnalysisResult:
        return PriceAnalysisResult(
            anomaly_detected=True, reasoning="Mock", risk_score=50
        )
    elif response_model == SellerAnalysisResult:
        return SellerAnalysisResult(
            reputation_risk="High", reasoning="Mock", risk_score=50
        )
    elif response_model == BrandAnalysisResult:
        return BrandAnalysisResult(
            authenticity_flags=["Mock"], reasoning="Mock", risk_score=50
        )
    elif response_model == ReviewAnalysisResult:
        return ReviewAnalysisResult(
            fake_reviews_detected=True, reasoning="Mock", risk_score=50
        )
    elif response_model == AIInvestigationResult:
        return AIInvestigationResult(
            summary="Mock",
            detailed_reasoning="Mock",
            suspicious_indicators=["Mock"],
            confidence_score=100.0,
        )
    return MagicMock()


@patch("backend.services.scraping_service.ScrapingService.scrape")
@patch("backend.services.llm_service.LLMService.generate_structured_response")
def test_investigation_service(mock_generate, mock_scrape):
    mock_scrape.return_value = get_mock_scraping_result()
    mock_generate.side_effect = get_mock_structured_response

    service = InvestigationService()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    report = service.run_investigation(request)

    assert report.risk_score == 100
    assert report.risk_level == "HIGH"
    assert report.confidence == 100.0
