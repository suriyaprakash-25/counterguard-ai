from backend.state import InvestigationState
from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry

@AgentRegistry.register("mystery_shopper")
class MysteryShopperAgent(BaseAgent):
    """
    Mystery Shopper agent pipeline stage.
        Poses as a buyer, requests authenticity proof from seller.
    """

    def __init__(self, cross_query_fn=None):
        self.cross_query_fn = cross_query_fn

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
