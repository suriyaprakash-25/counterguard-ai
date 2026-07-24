from backend.state import InvestigationState
from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry

@AgentRegistry.register("confidence")
class ConfidenceFusionAgent(BaseAgent):
    """
    Confidence Fusion agent pipeline stage.
        Aggregates evidence_timeline deltas into a labeled verdict.
    """

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
