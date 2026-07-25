from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.reporter import ReportGenerator
from backend.schemas.investigation import InvestigationReport, InvestigationRequest
from backend.services.scraping_service import ScrapingService


class InvestigationOrchestrator:
    def __init__(self):
        self.scraping_service = ScrapingService()
        self.analyzer = AnalyzerAgent()
        self.collector = EvidenceCollector()
        self.assessor = RiskAssessor()
        self.reporter = ReportGenerator()

    def run(self, request: InvestigationRequest) -> InvestigationReport:
        """
        Coordinates the execution of the multi-agent workflow.
        """
        scraping_result = self.scraping_service.scrape(request.listing_url)
        if not scraping_result.success:
            raise ValueError(f"Scraping failed: {scraping_result.error_message}")

        analysis = self.analyzer.analyze(request, scraping_result)
        evidence = self.collector.collect(analysis)
        risk = self.assessor.assess(analysis, evidence)
        report = self.reporter.generate(analysis, evidence, risk)

        return report
