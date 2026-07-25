import time
from backend.state import InvestigationState
from backend.services.investigation_factory import InvestigationFactory
from backend.orchestrator.graph import get_compiled_graph
from backend.logging import get_logger
from backend.exceptions import InvestigationExecutionError
from backend.types import JSONDict

logger = get_logger(__name__)

class InvestigationEngine:
    """
    Central engine for executing CounterGuard investigations.
    """
    
    def __init__(self):
        # We initialize the graph once per engine instance
        self.app = get_compiled_graph()
        
    def run(self, listing_id: str, listing_data: JSONDict = None) -> InvestigationState:
        """
        Executes a full investigation for a given listing.
        """
        logger.info(f"Investigation started for listing_id: {listing_id}")
        start_time = time.time()
        
        try:
            initial_state = InvestigationFactory.create_state(listing_id, listing_data)
            final_state = self.app.invoke(initial_state)
            
            execution_time = time.time() - start_time
            logger.info(f"Investigation finished for listing_id: {listing_id} in {execution_time:.4f} seconds")
            return final_state
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Investigation failed for listing_id: {listing_id} after {execution_time:.4f} seconds. Error: {str(e)}")
            raise InvestigationExecutionError(f"Execution failed: {str(e)}") from e
