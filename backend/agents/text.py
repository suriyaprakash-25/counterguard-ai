from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


@AgentRegistry.register("text")
class TextConsistencyAgent(BaseAgent):
    """
    Text Consistency agent pipeline stage.
        Compares spec/description vs. canonical catalog.
    """

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
