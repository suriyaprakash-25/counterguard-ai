import time

from backend.domain_types import JSONDict
from backend.exceptions import InvestigationExecutionError
from backend.log_config import get_logger
from backend.orchestrator.graph import get_compiled_graph
from backend.services.investigation_factory import InvestigationFactory
from backend.state import InvestigationState

logger = get_logger(__name__)


class InvestigationEngine:
    """
    Central engine for executing CounterGuard investigations.
    """

    def __init__(self):
        # We initialize the graph once per engine instance
        self.app = get_compiled_graph()

    def run(self, listing_id: str, listing_data: JSONDict = None) -> InvestigationState:
        logger.info(f"Engine starting execution for listing_id='{listing_id}'")
        start_time = time.time()

        initial_state = InvestigationFactory.create_state(listing_id, listing_data)

        try:
            # Execute the compiled LangGraph workflow synchronously
            final_state = self.app.invoke(initial_state)

            duration = time.time() - start_time
            logger.info(
                f"Engine execution completed for listing_id='{listing_id}' in {duration:.2f}s"
            )

            # Ensure final state has 'completed' status
            final_state["status"] = "completed"
            return final_state

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Engine execution failed for listing_id='{listing_id}' after {duration:.2f}s: {str(e)}",
                exc_info=True,
            )
            raise InvestigationExecutionError(
                f"Failed to execute investigation workflow for listing_id='{listing_id}': {str(e)}"
            ) from e
