from abc import ABC, abstractmethod

from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.raw_extraction import RawExtractionResult


class ExtractionProvider(ABC):
    """
    Abstract base interface for all official reference product extraction strategy providers.
    Enables specialized extraction strategies (HTML parsing, JSON-LD schema extraction,
    DOM selectors, or Direct APIs) without polluting the main ReferenceExtractionService.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique name of the extraction strategy provider."""
        pass

    @abstractmethod
    def extract(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> RawExtractionResult:
        """
        Extracts raw un-normalized product data from a candidate source.
        """
        pass

    async def extract_async(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> RawExtractionResult:
        """
        Asynchronously extracts raw product data. Default delegates to synchronous extract.
        """
        return self.extract(candidate=candidate, raw_content=raw_content)

    @abstractmethod
    def supports(self, candidate: SourceCandidate) -> bool:
        """
        Evaluates whether this provider strategy supports extracting the given SourceCandidate.
        """
        pass
