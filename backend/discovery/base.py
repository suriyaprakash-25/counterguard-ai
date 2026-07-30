from abc import ABC, abstractmethod
from typing import List

from backend.schemas.discovery import ListingCandidate


class BaseMarketplaceAdapter(ABC):
    """
    Abstract base interface for marketplace search adapters.
    Every supported marketplace (Amazon, Flipkart, Meesho, TradeIndia, AJIO, Myntra)
    must implement this interface.
    """

    @property
    @abstractmethod
    def marketplace_name(self) -> str:
        """Returns the canonical name of the marketplace (e.g., 'Amazon', 'Flipkart')."""
        pass

    @abstractmethod
    async def search_candidates(
        self, query: str, limit: int = 5
    ) -> List[ListingCandidate]:
        """
        Executes search for candidate listings matching the query.
        Returns a list of structured ListingCandidate objects.
        """
        pass
