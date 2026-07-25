from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.reporter import ReportGenerator
from backend.schemas.investigation import InvestigationReport, InvestigationRequest


class InvestigationOrchestrator:
    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.collector = EvidenceCollector()
        self.assessor = RiskAssessor()
        self.reporter = ReportGenerator()

    def run(self, request: InvestigationRequest) -> InvestigationReport:
        """
        Coordinates the execution of the multi-agent workflow.
        """
        analysis = self.analyzer.analyze(request)
        evidence = self.collector.collect(analysis)
        risk = self.assessor.assess(analysis, evidence)
        report = self.reporter.generate(analysis, evidence, risk)

        return report
