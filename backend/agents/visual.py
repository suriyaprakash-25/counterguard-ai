from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


@AgentRegistry.register("visual")
class VisualForensicsAgent(BaseAgent):
    """
    Visual Forensics agent pipeline stage.
        Checks image similarity against a golden reference.
    """

    def answer_query(self, question: str, state: InvestigationState) -> str:
        """
        Answers logo/packaging comparison requests from other agents.
        """
        return "visual_answer_placeholder"

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
