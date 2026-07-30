import logging
from typing import Any, Dict, Optional

from backend.schemas.official_product import OfficialProductProfile

logger = logging.getLogger(__name__)


class OfficialProductRegistry:
    """
    OfficialProductRegistry Interface (Sprint 17 Architecture Foundation)

    Defines the storage and retrieval repository contract for official product baseline profiles.
    Future implementations may back this interface with Redis caching or database persistence.

    PHASE 1 STATUS: Architectural interface definition only. In-memory dictionary stub.
    """

    def __init__(self):
        self._store: Dict[str, OfficialProductProfile] = {}
        logger.info("Initializing OfficialProductRegistry interface stub.")

    def get(self, product_key: str) -> Optional[OfficialProductProfile]:
        """
        Retrieves a cached OfficialProductProfile by product key.
        """
        clean_key = product_key.strip().lower()
        return self._store.get(clean_key)

    def put(self, product_key: str, profile: OfficialProductProfile) -> None:
        """
        Stores an OfficialProductProfile in the registry.
        """
        clean_key = product_key.strip().lower()
        self._store[clean_key] = profile
        logger.debug(
            f"[OfficialProductRegistry] Registered profile for key '{clean_key}'."
        )

    def update(self, product_key: str, updates: Dict[str, Any]) -> None:
        """
        Updates fields of an existing OfficialProductProfile.
        """
        clean_key = product_key.strip().lower()
        existing = self.get(clean_key)
        if existing:
            updated_data = existing.model_dump()
            updated_data.update(updates)
            self._store[clean_key] = OfficialProductProfile(**updated_data)
            logger.debug(
                f"[OfficialProductRegistry] Updated profile for key '{clean_key}'."
            )

    def invalidate(self, product_key: str) -> None:
        """
        Removes an entry from the registry cache.
        """
        clean_key = product_key.strip().lower()
        if clean_key in self._store:
            del self._store[clean_key]
            logger.debug(f"[OfficialProductRegistry] Invalidated key '{clean_key}'.")
