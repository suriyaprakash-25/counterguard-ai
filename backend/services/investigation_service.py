from backend.agents.orchestrator import InvestigationOrchestrator
from backend.schemas.investigation import InvestigationReport, InvestigationRequest


class InvestigationService:
    def __init__(self):
        self.orchestrator = InvestigationOrchestrator()

    def run_investigation(self, request: InvestigationRequest) -> InvestigationReport:
        """
        Receives request, invokes orchestrator, and returns report.
        """
        return self.orchestrator.run(request)
