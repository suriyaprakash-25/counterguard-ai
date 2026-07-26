import logging
from typing import Any, Dict, List, Optional

from backend.graph.models.domain import GraphNode, RelationshipType
from backend.graph.repositories.interfaces import GraphRepository
from backend.infrastructure.graph.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class Neo4jGraphRepository(GraphRepository):
    """
    Neo4j implementation of the GraphRepository.
    Receives a managed Neo4jClient instance via Dependency Injection.
    """

    def __init__(self, client: Neo4jClient):
        self.client = client
        if not self.client.is_connected:
            logger.warning(
                "GraphRepository initialized with a disconnected Neo4jClient. Operations will be mocked."
            )

    def health_check(self) -> bool:
        if not self.client.is_connected:
            return False

        try:
            with self.client.session() as session:
                result = session.run("RETURN 1 AS ok")
                record = result.single()
                return record["ok"] == 1 if record else False
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    def create_node(self, node: GraphNode) -> None:
        if not self.client.is_connected:
            return

        query = f"MERGE (n:{node.label} {{id: $id}}) " "SET n += $properties"
        with self.client.session() as session:
            session.run(query, id=node.id, properties=node.properties)

    def update_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> None:
        if not self.client.is_connected:
            return

        query = f"MATCH (n:{label} {{id: $id}}) " "SET n += $properties"
        with self.client.session() as session:
            session.run(query, id=node_id, properties=properties)

    def create_relationship(
        self,
        from_id: str,
        from_label: str,
        to_id: str,
        to_label: str,
        rel_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.client.is_connected:
            return

        properties = properties or {}
        query = (
            f"MATCH (a:{from_label} {{id: $from_id}}) "
            f"MATCH (b:{to_label} {{id: $to_id}}) "
            f"MERGE (a)-[r:{rel_type.value}]->(b) "
            "SET r += $properties"
        )
        with self.client.session() as session:
            session.run(query, from_id=from_id, to_id=to_id, properties=properties)

    def relationship_exists(
        self, from_id: str, to_id: str, rel_type: RelationshipType
    ) -> bool:
        if not self.client.is_connected:
            return False

        query = (
            f"MATCH ({{id: $from_id}})-[r:{rel_type.value}]->({{id: $to_id}}) "
            "RETURN count(r) > 0 AS exists"
        )
        with self.client.session() as session:
            result = session.run(query, from_id=from_id, to_id=to_id)
            record = result.single()
            return record["exists"] if record else False

    def get_node(self, node_id: str, label: str) -> Optional[GraphNode]:
        if not self.client.is_connected:
            return None

        query = f"MATCH (n:{label} {{id: $id}}) RETURN n"
        with self.client.session() as session:
            result = session.run(query, id=node_id)
            record = result.single()
            if record:
                node = record["n"]
                return GraphNode(id=node["id"], label=label, properties=dict(node))
        return None

    def delete_node(self, node_id: str, label: str) -> None:
        if not self.client.is_connected:
            return

        query = f"MATCH (n:{label} {{id: $id}}) DETACH DELETE n"
        with self.client.session() as session:
            session.run(query, id=node_id)

    def run_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.client.is_connected:
            return []

        parameters = parameters or {}
        with self.client.session() as session:
            result = session.run(query, parameters)
            return [dict(record) for record in result]
