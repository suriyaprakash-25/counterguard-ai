from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.graph.models.domain import GraphNode, RelationshipType


class GraphRepository(ABC):
    """Abstract interface for graph database operations."""

    @abstractmethod
    def create_node(self, node: GraphNode) -> None:
        """Creates or merges a node in the graph."""
        pass

    @abstractmethod
    def update_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> None:
        """Updates properties of an existing node."""
        pass

    @abstractmethod
    def create_relationship(
        self,
        from_id: str,
        from_label: str,
        to_id: str,
        to_label: str,
        rel_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Creates or merges a directed relationship between two nodes."""
        pass

    @abstractmethod
    def relationship_exists(
        self, from_id: str, to_id: str, rel_type: RelationshipType
    ) -> bool:
        """Checks if a relationship exists between two nodes."""
        pass

    @abstractmethod
    def get_node(self, node_id: str, label: str) -> Optional[GraphNode]:
        """Retrieves a node by its ID and label."""
        pass

    @abstractmethod
    def delete_node(self, node_id: str, label: str) -> None:
        """Deletes a node and all its relationships."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Executes a simple query to verify graph connection is active."""
        pass

    @abstractmethod
    def run_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Executes a raw graph query (e.g. Cypher). Used internally by specialized services."""
        pass
