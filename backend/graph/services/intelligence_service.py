import logging
from typing import Any, Dict, List

from backend.graph.analytics.metrics import GraphMetrics
from backend.graph.models.domain import GraphNode
from backend.graph.repositories.interfaces import GraphRepository

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Executes business logic to discover connected intelligence across the knowledge graph.
    All Cypher queries and graph traversals are encapsulated here through the repository.
    """

    def __init__(self, repository: GraphRepository):
        self.repository = repository

    def find_connected_network(self, seller_name: str) -> Dict[str, Any]:
        """
        Finds the 2-hop neighborhood of a seller to uncover their extended network,
        including shared phones, emails, addresses, and other connected sellers.
        """
        seller_id = f"seller_{seller_name.lower().replace(' ', '_')}"

        # Cypher query to find all nodes up to 2 hops away from the given seller
        query = """
        MATCH (s:Seller {id: $seller_id})-[*1..2]-(connected)
        WHERE NOT connected:Investigation
        RETURN connected.id AS id, labels(connected)[0] AS label, connected AS properties
        """

        try:
            results = self.repository.run_query(query, {"seller_id": seller_id})

            network = {"nodes": [], "labels": set()}

            for row in results:
                node = GraphNode(
                    id=row["id"], label=row["label"], properties=dict(row["properties"])
                )
                network["nodes"].append(node.model_dump())
                network["labels"].add(row["label"])

            network["labels"] = list(network["labels"])
            return network
        except Exception as e:
            logger.error(f"Failed to find connected network for {seller_name}: {e}")
            return {"nodes": [], "labels": []}

    def find_shared_identifiers(self, seller_name: str) -> Dict[str, List[str]]:
        """
        Specifically looks for phones, emails, and images shared with OTHER sellers.
        """
        seller_id = f"seller_{seller_name.lower().replace(' ', '_')}"

        query = """
        MATCH (s:Seller {id: $seller_id})-[:USES_PHONE|USES_EMAIL|USES_ADDRESS|USES_IMAGE]->(identifier)<-[:USES_PHONE|USES_EMAIL|USES_ADDRESS|USES_IMAGE]-(other:Seller)
        RETURN labels(identifier)[0] AS type, identifier.id AS id, other.name AS shared_with
        """

        try:
            results = self.repository.run_query(query, {"seller_id": seller_id})

            shared = {
                "Phone": [],
                "Email": [],
                "Address": [],
                "Image": [],
                "Sellers": set(),
            }

            for row in results:
                id_type = row["type"]
                if id_type in shared:
                    shared[id_type].append(row["id"])
                shared["Sellers"].add(row["shared_with"])

            shared["Sellers"] = list(shared["Sellers"])
            return shared
        except Exception as e:
            logger.error(f"Failed to find shared identifiers for {seller_name}: {e}")
            return {}

    def calculate_seller_network_risk(self, seller_name: str) -> float:
        """
        Determines the risk multiplier for a seller based on the historical verdicts
        of the sellers they are connected to in the graph.
        """
        seller_id = f"seller_{seller_name.lower().replace(' ', '_')}"

        # Find all investigations linked to sellers in this seller's 2-hop network
        query = """
        MATCH (s:Seller {id: $seller_id})-[:USES_PHONE|USES_EMAIL|USES_ADDRESS|USES_IMAGE*1..2]-(other:Seller)<-[:INVESTIGATED_IN]-(inv:Investigation)
        RETURN inv
        """

        try:
            results = self.repository.run_query(query, {"seller_id": seller_id})
            investigations = [
                GraphNode(
                    id=r["inv"]["id"], label="Investigation", properties=dict(r["inv"])
                )
                for r in results
            ]

            # Use metrics engine to calculate risk
            return GraphMetrics.calculate_network_risk(
                sellers=[], investigations=investigations
            )
        except Exception as e:
            logger.error(f"Failed to calculate network risk for {seller_name}: {e}")
            return 1.0

    def generate_graph_summary(self, seller_name: str) -> Dict[str, Any]:
        """
        Generates a complete graph intelligence summary for use in LangGraph context.
        """
        return {
            "network_size": len(
                self.find_connected_network(seller_name).get("nodes", [])
            ),
            "shared_identifiers": self.find_shared_identifiers(seller_name),
            "network_risk_multiplier": self.calculate_seller_network_risk(seller_name),
        }
