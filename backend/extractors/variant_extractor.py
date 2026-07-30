import logging
from typing import List, Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class VariantExtractor(FieldExtractor):
    """Extracts raw variant color/size options and produces traceable ExtractionEvidence."""

    @property
    def target_field(self) -> str:
        return "variants"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[List[str], Optional[ExtractionEvidence]]:
        variants = candidate.metadata.get("variants", [])
        evidence = None
        if variants:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=variants,
                css_selector=".swatch-option, select.variant-selector",
                xpath="//div[contains(@class, 'variant')]",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=candidate.confidence,
            )
        return variants, evidence
