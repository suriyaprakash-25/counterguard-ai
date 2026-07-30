import logging
from typing import Any, Dict, Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class SpecificationExtractor(FieldExtractor):
    """Extracts raw technical specifications dictionary and produces traceable ExtractionEvidence."""

    @property
    def target_field(self) -> str:
        return "specifications"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Dict[str, Any], Optional[ExtractionEvidence]]:
        specs = candidate.metadata.get("specifications", {"domain": candidate.domain})
        evidence = ExtractionEvidence(
            field=self.target_field,
            value=specs,
            css_selector="table.specs-table, dl.tech-specs",
            xpath="//table[contains(@class, 'specs')]",
            source_url=candidate.url,
            provider=candidate.provider,
            confidence=candidate.confidence,
        )
        return specs, evidence
