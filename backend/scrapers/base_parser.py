from abc import ABC, abstractmethod

from backend.schemas.scraping import ParsedListing


class BaseParser(ABC):
    @abstractmethod
    def parse(self, html: str, url: str) -> ParsedListing:
        """
        Extracts structured data from HTML content.
        """
        pass
