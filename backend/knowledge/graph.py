import logging
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Dict, List, Optional, Set

from backend.knowledge.entities import Entity
from backend.knowledge.exceptions import (
    EntityNotFoundError,
    RelationshipInvalidError,
)
from backend.knowledge.relationships import Relationship

logger = logging.getLogger(__name__)


class KnowledgeGraphInterface(ABC):
    """
    Abstract interface contract for CounterGuard Knowledge Graphs.
    Defines foundational operations for entity node and relational edge lifecycle management,
    neighborhood querying, and path discovery without dependence on AI or LLM agents.
    """

    @abstractmethod
    def add_entity(self, entity: Entity) -> None:
        """Add or update an entity node within the graph."""
        pass

    @abstractmethod
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by its unique identifier."""
        pass

    @abstractmethod
    def delete_entity(self, entity_id: str) -> None:
        """Delete an entity node and automatically purge all associated relationships."""
        pass

    @abstractmethod
    def list_entities(self, entity_type: Optional[str] = None) -> List[Entity]:
        """List all entities, optionally filtered by entity_type."""
        pass

    @abstractmethod
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a directed relationship between two existing entity nodes in the graph."""
        pass

    @abstractmethod
    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        """Retrieve a specific relationship edge by its unique ID."""
        pass

    @abstractmethod
    def delete_relationship(self, rel_id: str) -> None:
        """Remove a relationship edge from the graph."""
        pass

    @abstractmethod
    def list_relationships(
        self, relationship_type: Optional[str] = None
    ) -> List[Relationship]:
        """List all relationships, optionally filtered by relationship_type."""
        pass

    @abstractmethod
    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
    ) -> List[Entity]:
        """
        Retrieve adjacent neighboring entities connected to a target node.
        Direction can be 'out' (outgoing), 'in' (incoming), or 'both'.
        """
        pass

    @abstractmethod
    def find_paths(
        self, start_entity_id: str, end_entity_id: str, max_depth: int = 4
    ) -> List[List[str]]:
        """Discover all valid connecting paths between two nodes up to max_depth hops."""
        pass

    @abstractmethod
    def get_subgraph(self, entity_id: str, max_depth: int = 1) -> Dict[str, Any]:
        """Extract an egocentric subgraph dictionary centered on a target seed node up to max_depth."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all entity nodes and relationship edges from the graph."""
        pass


class InMemoryKnowledgeGraph(KnowledgeGraphInterface):
    """
    In-memory lightweight Knowledge Graph implementation for CounterGuard investigations.
    Provides fast graph traversal, path finding, and egocentric network extraction.
    """

    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}
        self._relationships: Dict[str, Relationship] = {}
        self._out_edges: Dict[str, List[str]] = {}
        self._in_edges: Dict[str, List[str]] = {}

    def add_entity(self, entity: Entity) -> None:
        if not entity.id or not str(entity.id).strip():
            raise ValueError("Entity ID cannot be empty.")
        entity_id = entity.id
        self._entities[entity_id] = entity
        if entity_id not in self._out_edges:
            self._out_edges[entity_id] = []
        if entity_id not in self._in_edges:
            self._in_edges[entity_id] = []
        logger.debug(
            f"Added entity node '{entity_id}' (type: {entity.entity_type}) to graph."
        )

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def delete_entity(self, entity_id: str) -> None:
        if entity_id not in self._entities:
            raise EntityNotFoundError(f"Entity '{entity_id}' does not exist in graph.")

        # Remove all outgoing edges
        for rel_id in list(self._out_edges.get(entity_id, [])):
            self.delete_relationship(rel_id)
        # Remove all incoming edges
        for rel_id in list(self._in_edges.get(entity_id, [])):
            self.delete_relationship(rel_id)

        del self._entities[entity_id]
        if entity_id in self._out_edges:
            del self._out_edges[entity_id]
        if entity_id in self._in_edges:
            del self._in_edges[entity_id]
        logger.debug(f"Deleted entity node '{entity_id}' and all attached edges.")

    def list_entities(self, entity_type: Optional[str] = None) -> List[Entity]:
        if entity_type:
            target_type = entity_type.upper().strip()
            return [
                ent
                for ent in self._entities.values()
                if ent.entity_type.upper() == target_type
            ]
        return list(self._entities.values())

    def add_relationship(self, relationship: Relationship) -> None:
        if relationship.source_id not in self._entities:
            raise RelationshipInvalidError(
                f"Source entity '{relationship.source_id}' not found in graph."
            )
        if relationship.target_id not in self._entities:
            raise RelationshipInvalidError(
                f"Target entity '{relationship.target_id}' not found in graph."
            )

        rel_id = relationship.id
        self._relationships[rel_id] = relationship

        if rel_id not in self._out_edges[relationship.source_id]:
            self._out_edges[relationship.source_id].append(rel_id)
        if rel_id not in self._in_edges[relationship.target_id]:
            self._in_edges[relationship.target_id].append(rel_id)

        logger.debug(
            f"Added relationship edge '{rel_id}' ({relationship.relationship_type}) to graph."
        )

    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        return self._relationships.get(rel_id)

    def delete_relationship(self, rel_id: str) -> None:
        rel = self._relationships.get(rel_id)
        if not rel:
            return
        source_id = rel.source_id
        target_id = rel.target_id

        if source_id in self._out_edges and rel_id in self._out_edges[source_id]:
            self._out_edges[source_id].remove(rel_id)
        if target_id in self._in_edges and rel_id in self._in_edges[target_id]:
            self._in_edges[target_id].remove(rel_id)

        del self._relationships[rel_id]
        logger.debug(f"Deleted relationship edge '{rel_id}'.")

    def list_relationships(
        self, relationship_type: Optional[str] = None
    ) -> List[Relationship]:
        if relationship_type:
            target_rel = relationship_type.upper().strip()
            return [
                r
                for r in self._relationships.values()
                if r.relationship_type.upper() == target_rel
            ]
        return list(self._relationships.values())

    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
    ) -> List[Entity]:
        if entity_id not in self._entities:
            raise EntityNotFoundError(f"Entity '{entity_id}' does not exist in graph.")

        neighbor_ids: Set[str] = set()
        direction_clean = direction.lower().strip()
        target_type = relationship_type.upper().strip() if relationship_type else None

        # Check outgoing edges (source -> target)
        if direction_clean in ["out", "both", "outgoing"]:
            for rel_id in self._out_edges.get(entity_id, []):
                rel = self._relationships[rel_id]
                if not target_type or rel.relationship_type.upper() == target_type:
                    neighbor_ids.add(rel.target_id)

        # Check incoming edges (source -> target where entity_id is target)
        if direction_clean in ["in", "both", "incoming"]:
            for rel_id in self._in_edges.get(entity_id, []):
                rel = self._relationships[rel_id]
                if not target_type or rel.relationship_type.upper() == target_type:
                    neighbor_ids.add(rel.source_id)

        return [self._entities[nid] for nid in neighbor_ids if nid in self._entities]

    def _validate_endpoints(self, start_id: str, end_id: str) -> None:
        if start_id not in self._entities:
            raise EntityNotFoundError(f"Start entity '{start_id}' not found.")
        if end_id not in self._entities:
            raise EntityNotFoundError(f"End entity '{end_id}' not found.")

    def find_paths(
        self, start_entity_id: str, end_entity_id: str, max_depth: int = 4
    ) -> List[List[str]]:
        self._validate_endpoints(start_entity_id, end_entity_id)
        if max_depth <= 0:
            return []
        if start_entity_id == end_entity_id:
            return [[start_entity_id]]

        found_paths: List[List[str]] = []
        queue: deque[List[str]] = deque([[start_entity_id]])

        while queue:
            current_path = queue.popleft()
            if len(current_path) - 1 >= max_depth:
                continue
            self._expand_path(
                current_path, end_entity_id, max_depth, queue, found_paths
            )

        return found_paths

    def _expand_path(
        self,
        current_path: List[str],
        end_id: str,
        max_depth: int,
        queue: deque[List[str]],
        found_paths: List[List[str]],
    ) -> None:
        current_node = current_path[-1]
        for neighbor in self.get_neighbors(current_node, direction="both"):
            if neighbor.id in current_path:
                continue  # Avoid cycles
            new_path = current_path + [neighbor.id]
            if neighbor.id == end_id:
                found_paths.append(new_path)
            elif len(new_path) - 1 < max_depth:
                queue.append(new_path)

    def get_subgraph(self, entity_id: str, max_depth: int = 1) -> Dict[str, Any]:
        if entity_id not in self._entities:
            raise EntityNotFoundError(f"Entity '{entity_id}' does not exist in graph.")

        visited_nodes: Set[str] = {entity_id}
        visited_edges: Set[str] = set()
        queue: deque[tuple[str, int]] = deque([(entity_id, 0)])

        while queue:
            curr_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            # Check outgoing
            for rel_id in self._out_edges.get(curr_id, []):
                visited_edges.add(rel_id)
                rel = self._relationships[rel_id]
                if rel.target_id not in visited_nodes:
                    visited_nodes.add(rel.target_id)
                    queue.append((rel.target_id, depth + 1))

            # Check incoming
            for rel_id in self._in_edges.get(curr_id, []):
                visited_edges.add(rel_id)
                rel = self._relationships[rel_id]
                if rel.source_id not in visited_nodes:
                    visited_nodes.add(rel.source_id)
                    queue.append((rel.source_id, depth + 1))

        nodes_data = [
            self._entities[nid].model_dump()
            for nid in visited_nodes
            if nid in self._entities
        ]
        edges_data = [
            self._relationships[eid].model_dump()
            for eid in visited_edges
            if eid in self._relationships
        ]

        return {
            "root_id": entity_id,
            "max_depth": max_depth,
            "nodes": nodes_data,
            "edges": edges_data,
        }

    def clear(self) -> None:
        self._entities.clear()
        self._relationships.clear()
        self._out_edges.clear()
        self._in_edges.clear()
        logger.info("Knowledge Graph in-memory structures cleared.")


# Clean alias for general consumer application usage
KnowledgeGraph = InMemoryKnowledgeGraph
