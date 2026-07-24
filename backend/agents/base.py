from abc import ABC, abstractmethod
from backend.state import InvestigationState

class BaseAgent(ABC):
    """
    Base class for all CounterGuard agents.
    """

    @abstractmethod
    def run(self, state: InvestigationState) -> InvestigationState:
        """
        Execute the agent's main logic.
        """
        pass
