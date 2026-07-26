"""
CounterGuard Lightweight Knowledge Graph Layer.

Provides structured entity node representations, semantic relationship tracking, and fast in-memory graph operations
(neighborhood queries, path discovery, subgraph extraction) without dependency on AI agents or LLMs.
"""

from backend.knowledge.entities import (
    Brand,
    Email,
    Entity,
    Image,
    Listing,
    Phone,
    Seller,
)
from backend.knowledge.exceptions import (
    EntityNotFoundError,
    KnowledgeGraphError,
    RelationshipInvalidError,
)
from backend.knowledge.graph import (
    InMemoryKnowledgeGraph,
    KnowledgeGraph,
    KnowledgeGraphInterface,
)
from backend.knowledge.relationships import (
    Relationship,
    RelationshipType,
    create_relationship,
)

__all__ = [
    # Entities
    "Entity",
    "Seller",
    "Brand",
    "Listing",
    "Phone",
    "Email",
    "Image",
    # Relationships
    "Relationship",
    "RelationshipType",
    "create_relationship",
    # Graph Implementations & Interfaces
    "KnowledgeGraphInterface",
    "InMemoryKnowledgeGraph",
    "KnowledgeGraph",
    # Exceptions
    "KnowledgeGraphError",
    "EntityNotFoundError",
    "RelationshipInvalidError",
]
