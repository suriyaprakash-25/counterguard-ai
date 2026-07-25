from langgraph.graph import StateGraph

from backend.state import InvestigationState


def build_graph() -> StateGraph:
    """
    Builds and returns the LangGraph StateGraph instance.
    """
    graph = StateGraph(InvestigationState)
    # Placeholder for graph wiring
    return graph
