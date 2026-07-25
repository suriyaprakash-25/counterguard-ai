from langgraph.graph import StateGraph

from langgraph.graph import END, StateGraph

# Ensure the ScoutAgent is registered before retrieving
import backend.agents.scout  # noqa: F401
from backend.agents.registry import AgentRegistry
from backend.state import InvestigationState


def build_graph() -> StateGraph:
    """
    Builds and returns the LangGraph StateGraph instance.
    Currently only wires the Scout node.
    """
    graph = StateGraph(InvestigationState)

    # Retrieve and instantiate agent
    scout_class = AgentRegistry.get_agent("scout")
    scout_agent = scout_class()

    # Add nodes
    graph.add_node("scout", scout_agent.run)

    # Wire the pipeline
    graph.set_entry_point("scout")
    graph.add_edge("scout", END)
    return graph
