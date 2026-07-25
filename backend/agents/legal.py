from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


@AgentRegistry.register("legal")
class LegalEscalationAgent(BaseAgent):
    """
    Legal Escalation agent pipeline stage.
        Drafts takedown notice, never auto-files.
    """

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
