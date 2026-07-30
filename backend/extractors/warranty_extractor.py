import logging
from typing import Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class WarrantyExtractor(FieldExtractor):
    """Extracts raw warranty text snippets and produces traceable ExtractionEvidence."""

    @property
    def target_field(self) -> str:
        return "warranty"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[str], Optional[ExtractionEvidence]]:
        warranty_text = candidate.metadata.get("warranty_text")
        evidence = None
        if warranty_text:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=warranty_text,
                css_selector=".warranty-info, div[data-warranty]",
                xpath="//div[contains(@class, 'warranty')]",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=candidate.confidence,
            )
        return warranty_text, evidence
