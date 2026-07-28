from backend.orchestrator.builder import build_graph


def test_orchestrator_automation_nodes():
    """
    Verifies that the orchestrator graph compiles with the streamlined pipeline.
    """
    graph = build_graph()

    # Check core pipeline nodes are present
    assert "scraper" in graph.nodes
    assert "analyzer" in graph.nodes
    assert "collector" in graph.nodes
    assert "assessor" in graph.nodes
    assert "planner" in graph.nodes
    assert "coordinator" in graph.nodes
    assert "trusted_product" in graph.nodes
    assert "reporter" in graph.nodes

    # Assert that reporter routes directly to END
    edges = graph.edges
    has_reporter_to_end = any(
        source == "reporter" and target == "__end__" for source, target in edges
    )
    assert has_reporter_to_end
