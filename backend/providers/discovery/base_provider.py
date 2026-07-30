from abc import ABC, abstractmethod
from typing import List

from backend.schemas.discovery_engine import SourceCandidate


class SearchProvider(ABC):
    """
    Abstract base interface for all product reference discovery search providers.
    Designed for zero provider-specific assumptions, enabling seamless integration of
    Static Catalog, Tavily, SerpAPI, Google CSE, Firecrawl, Crawl4AI, or internal registries.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique name identifier of the discovery provider."""
        pass

    @abstractmethod
    def search(self, query: str, brand: str = "") -> List[SourceCandidate]:
        """
        Synchronously searches for reference product source candidates.
        """
        pass

    async def search_async(self, query: str, brand: str = "") -> List[SourceCandidate]:
        """
        Asynchronously searches for reference product source candidates.
        Default implementation delegates to synchronous search.
        """
        return self.search(query=query, brand=brand)

    @abstractmethod
    def supports(self, brand: str, domain: str = "") -> bool:
        """
        Evaluates whether this provider supports discovery for the given brand or domain.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Performs a health and connectivity check for the provider.
        """
        pass
