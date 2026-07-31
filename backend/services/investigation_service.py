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
        import uuid

        corr_id = f"corr-{uuid.uuid4().hex[:8]}"
        logger.info(
            f"Starting InvestigationService [{corr_id}] for {request.listing_url}"
        )

        initial_state: InvestigationState = {
            "request": request,
            "correlation_id": corr_id,
            "investigation_timeline": [],
            "execution_telemetry": {},
        }

        try:
            # Search organizational memory precedents before final report generation
            try:
                from backend.agents.historical_memory_agent import (
                    historical_memory_agent,
                )

                search_query = (
                    getattr(request, "raw_text", None)
                    or getattr(request, "listing_url", None)
                    or "Counterfeit Audit"
                )
                mem_resp = historical_memory_agent.search_similar_investigations(
                    search_query
                )
                logger.info(
                    f"[InvestigationService] Pre-investigation organizational memory search: {mem_resp.total_matches} precedents found."
                )
            except Exception as mem_err:
                logger.warning(
                    f"[InvestigationService] Organizational memory search fallback: {mem_err}"
                )

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
