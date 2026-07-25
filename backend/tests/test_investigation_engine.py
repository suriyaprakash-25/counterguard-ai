from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.orchestrator import InvestigationOrchestrator
from backend.agents.reporter import ReportGenerator
from backend.schemas.investigation import InvestigationRequest
from backend.services.investigation_service import InvestigationService


def test_analyzer():
    analyzer = AnalyzerAgent()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    result = analyzer.analyze(request)
    assert result.brand == "GenericBrand"
    assert result.marketplace == "Amazon"
    assert result.price == 45.0
    assert result.seller_rating == 2.5
    assert "low_price" in result.risk_signals


def test_collector():
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    analysis = analyzer.analyze(request)
    evidence = collector.collect(analysis)
    assert evidence.price_anomaly is True
    assert evidence.seller_reputation == "Poor"
    assert evidence.missing_warranty is True
    assert evidence.listing_quality == "poor"


def test_assessor():
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    assessor = RiskAssessor()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    analysis = analyzer.analyze(request)
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
    analysis = analyzer.analyze(request)
    evidence = collector.collect(analysis)
    risk = assessor.assess(analysis, evidence)
    report = reporter.generate(analysis, evidence, risk)

    assert report.risk_score == 100
    assert report.risk_level == "HIGH"
    assert "Suspiciously low price detected" in report.findings[0]
    assert report.recommendation == "Immediate takedown recommended."


def test_orchestrator():
    orchestrator = InvestigationOrchestrator()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    report = orchestrator.run(request)

    assert report.risk_score == 100
    assert report.risk_level == "HIGH"


def test_investigation_service():
    service = InvestigationService()
    request = InvestigationRequest(
        listing_url="http://example.com", marketplace="Amazon"
    )
    report = service.run_investigation(request)

    assert report.risk_score == 100
    assert report.risk_level == "HIGH"
