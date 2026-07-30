import logging
from typing import List, Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class ImageExtractor(FieldExtractor):
    """Extracts raw image URLs and produces traceable ExtractionEvidence."""

    @property
    def target_field(self) -> str:
        return "images"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[List[str], Optional[ExtractionEvidence]]:
        images = candidate.metadata.get("official_images", [])
        evidence = None
        if images:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=images,
                css_selector="img.gallery-image, img[data-zoom]",
                xpath="//img[contains(@class, 'gallery')]",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=candidate.confidence,
            )
        return images, evidence
