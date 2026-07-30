from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence


class FieldExtractor(ABC):
    """
    Abstract base interface for modular, field-specific extractors.
    Decouples single-field parsing logic (Title, Price, Specs, Images, Variants, Warranty, Certification)
    from ExtractionProvider strategy implementations.
    """

    @property
    @abstractmethod
    def target_field(self) -> str:
        """Name of the field being extracted (e.g. 'title', 'price', 'specifications')."""
        pass

    @abstractmethod
    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[Any], Optional[ExtractionEvidence]]:
        """
        Extracts the specific field and returns a Tuple[ExtractedValue, ExtractionEvidence].
        """
        pass
