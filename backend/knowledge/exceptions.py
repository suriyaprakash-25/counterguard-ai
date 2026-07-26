from backend.exceptions import CounterGuardError


class KnowledgeGraphError(CounterGuardError):
    """Base exception class for all errors originating within the Knowledge Graph."""

    pass


class EntityNotFoundError(KnowledgeGraphError):
    """Raised when an entity operation is attempted on a non-existent node ID."""

    pass


class RelationshipInvalidError(KnowledgeGraphError):
    """Raised when an invalid relationship is created or references missing source/target nodes."""

    pass
