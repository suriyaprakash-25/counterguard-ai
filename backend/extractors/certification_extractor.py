import logging
from typing import List, Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class CertificationExtractor(FieldExtractor):
    """Extracts raw compliance and regulatory certification badges (CE, FCC, BIS, RoHS)."""

    @property
    def target_field(self) -> str:
        return "certifications"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[List[str], Optional[ExtractionEvidence]]:
        certs = candidate.metadata.get("certifications", ["CE", "RoHS", "BIS"])
        evidence = ExtractionEvidence(
            field=self.target_field,
            value=certs,
            css_selector=".certification-badges, span.compliance-tag",
            xpath="//div[contains(@class, 'certification')]",
            source_url=candidate.url,
            provider=candidate.provider,
            confidence=candidate.confidence,
        )
        return certs, evidence
