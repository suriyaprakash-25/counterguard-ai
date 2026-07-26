from typing import Dict, List

from backend.graph.models.domain import GraphNode


class GraphMetrics:
    """Provides standard graph analytics utilities on a given set of nodes and edges."""

    @staticmethod
    def calculate_degree_centrality(connections: List[Dict]) -> Dict[str, int]:
        """Calculates simple degree centrality (number of connections) for nodes."""
        centrality = {}
        for conn in connections:
            for node_id in [conn.get("node1_id"), conn.get("node2_id")]:
                if node_id:
                    centrality[node_id] = centrality.get(node_id, 0) + 1
        return centrality

    @staticmethod
    def calculate_network_risk(
        sellers: List[GraphNode], investigations: List[GraphNode]
    ) -> float:
        """
        Calculates a risk multiplier based on the number of connected counterfeit sellers.
        """
        if not sellers and not investigations:
            return 1.0

        counterfeit_count = 0
        for inv in investigations:
            if inv.properties.get("verdict") == "Counterfeit":
                counterfeit_count += 1

        # Base risk is 1.0, adds 0.2 for each counterfeit investigation in the network
        return min(1.0 + (counterfeit_count * 0.2), 2.0)
