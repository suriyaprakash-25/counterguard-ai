from backend.state import InvestigationState
from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.utils.timeline import log_event
from backend.logging import get_logger

logger = get_logger(__name__)

@AgentRegistry.register("scout")
class ScoutAgent(BaseAgent):
    """
    Scout agent pipeline stage.
    Detects new or changed listings.
        Detects new or changed listings.
    """

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        listing_id = state.get("listing_id")
        
        if not listing_id:
            logger.error("ScoutAgent failed: listing_id is missing.")
            raise ValueError("listing_id is required in the state")

        listing_data = state.get("listing_data", {})
        
        logger.info(f"Scout processing listing: {listing_id}")

        log_event(
            state=state,
            agent="scout",
            action="discovered_listing",
            detail=f"New/changed listing detected: {listing_id}",
            confidence_delta=0.0
        )
        
        if "agent_findings" not in state:
            state["agent_findings"] = {}
            
        state["agent_findings"]["scout"] = {
            "processed": True,
            "data_keys": list(listing_data.keys())
        }
        
        return state
