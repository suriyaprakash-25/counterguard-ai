from abc import ABC, abstractmethod
from typing import List, Optional

from backend.memory.models.domain import (
    InvestigationEpisode,
    SellerProfile,
)


class InvestigationRepository(ABC):
    """Abstract repository for persisting investigation episodes."""

    @abstractmethod
    def save(self, episode: InvestigationEpisode) -> None:
        pass

    @abstractmethod
    def get_by_id(self, episode_id: str) -> Optional[InvestigationEpisode]:
        pass

    @abstractmethod
    def delete(self, episode_id: str) -> None:
        pass

    @abstractmethod
    def list_recent(self, limit: int = 10) -> List[InvestigationEpisode]:
        pass


class SellerRepository(ABC):
    """Abstract repository for persisting seller profiles."""

    @abstractmethod
    def save(self, profile: SellerProfile) -> None:
        pass

    @abstractmethod
    def get_by_identity(
        self, name: str, domain: Optional[str] = None
    ) -> Optional[SellerProfile]:
        pass

    @abstractmethod
    def search(self, query: str) -> List[SellerProfile]:
        pass
