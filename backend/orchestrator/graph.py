from backend.orchestrator.builder import build_graph


def get_compiled_graph():
    """
    Returns the compiled LangGraph execution graph.
    """
    graph = build_graph()
    return graph.compile()
