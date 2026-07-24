from typing import Dict, Type
from backend.agents.base import BaseAgent

class AgentRegistry:
    """
    Registry for all CounterGuard agents.
    """
    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(agent_class: Type[BaseAgent]):
            cls._agents[name] = agent_class
            return agent_class
        return decorator

    @classmethod
    def get_agent(cls, name: str) -> Type[BaseAgent]:
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return cls._agents[name]
