from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


@AgentRegistry.register("scout")
class ScoutAgent(BaseAgent):
    """
    Scout agent pipeline stage.
        Detects new or changed listings.
    """

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
