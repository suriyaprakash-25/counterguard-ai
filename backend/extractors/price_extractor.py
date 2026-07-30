import logging
from typing import Optional, Tuple

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class PriceExtractor(FieldExtractor):
    """Extracts raw price string and produces traceable ExtractionEvidence."""

    @property
    def target_field(self) -> str:
        return "price"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[str], Optional[ExtractionEvidence]]:
        price_str = candidate.metadata.get("raw_price_str")
        evidence = None
        if price_str:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=price_str,
                css_selector=".price, .product-price, span[data-price]",
                xpath="//span[contains(@class, 'price')]",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=candidate.confidence,
            )
        return price_str, evidence
