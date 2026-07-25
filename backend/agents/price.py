from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


@AgentRegistry.register("price")
class PriceAnomalyAgent(BaseAgent):
    """
    Price Anomaly agent pipeline stage.
        Statistical pricing/discount outlier detection.
    """

    def answer_query(self, question: str, state: InvestigationState) -> str:
        """
        Answers conditional 'what-if' pricing questions from other agents.
        """
        return "price_answer_placeholder"

    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        return state
