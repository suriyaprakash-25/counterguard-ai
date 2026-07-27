from backend.orchestrator.builder import build_graph


def test_orchestrator_automation_nodes():
    """
    Verifies that the orchestrator graph includes the new automation nodes.
    """
    graph = build_graph()

    # Check that alert node is present
    assert "alert" in graph.nodes
    assert "save_memory" in graph.nodes

    # Check routing structure
    edges = graph.edges

    # Assert that reporter goes to save_memory, and save_memory goes to alert
    has_save_memory_to_alert = any(
        source == "save_memory" and target == "alert" for source, target in edges
    )
    assert has_save_memory_to_alert

    has_alert_to_end = any(
        source == "alert" and target == "__end__" for source, target in edges
    )
    assert has_alert_to_end
