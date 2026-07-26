import logging

from backend.exceptions import CounterGuardError
from backend.schemas.investigation import InvestigationReport, InvestigationRequest
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


class InvestigationService:
    def __init__(self):
        # The graph will be built on demand
        self.graph = None

    def run_investigation(self, request: InvestigationRequest) -> InvestigationReport:
        from backend.orchestrator.graph import get_compiled_graph

        graph = get_compiled_graph()
        """
        Executes the LangGraph multi-agent investigation workflow.
        """
        logger.info(f"Starting InvestigationService for {request.listing_url}")

        initial_state: InvestigationState = {"request": request}

        try:
            # LangGraph's invoke returns the final state dict
            final_state = graph.invoke(initial_state)

            if "report" not in final_state:
                raise CounterGuardError(
                    "Investigation completed but no report was generated."
                )

            return final_state["report"]
        except Exception as e:
            logger.error(f"Investigation execution failed: {e}")
            raise e
