from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


@AgentRegistry.register("seller_graph")
class SellerNetworkGraphAgent(BaseAgent):
    """
    Seller Network Graph agent pipeline stage.
        Community detection across seller registration data.
    """

    def __init__(self, cross_query_fn=None):
        self.cross_query_fn = cross_query_fn

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
