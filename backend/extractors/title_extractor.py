import logging
from typing import Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class TitleExtractor(FieldExtractor):
    """Extracts raw product title and produces traceable ExtractionEvidence."""

    @property
    def target_field(self) -> str:
        return "title"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[str], Optional[ExtractionEvidence]]:
        title_val = candidate.title or "Unknown Product Title"
        evidence = ExtractionEvidence(
            field=self.target_field,
            value=title_val,
            css_selector="h1.product-title, head > title",
            xpath="//h1[contains(@class, 'title')]",
            source_url=candidate.url,
            provider=candidate.provider,
            confidence=candidate.confidence,
        )
        return title_val, evidence
