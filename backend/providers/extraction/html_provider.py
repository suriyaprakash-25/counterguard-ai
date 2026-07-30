import logging
import time

from backend.providers.extraction.base_provider import ExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.raw_extraction import RawExtractionResult

logger = logging.getLogger(__name__)


class HTMLExtractionProvider(ExtractionProvider):
    """
    HTMLExtractionProvider (Strategy Provider)

    Extracts raw product metadata from HTML markup using DOM CSS selectors / BeautifulSoup.
    """

    @property
    def provider_name(self) -> str:
        return "HTMLExtractionProvider"

    def supports(self, candidate: SourceCandidate) -> bool:
        # Default fallback extraction strategy for any web candidate
        return True

    def extract(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> RawExtractionResult:
        start_time = time.time()
        logger.debug(f"[{self.provider_name}] Extracting from URL '{candidate.url}'.")

        # Extraction stub for foundation phase
        raw_title = candidate.title or "Unknown Product Title"
        brand_name = candidate.metadata.get("brand_key", "Generic Brand")

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

        return RawExtractionResult(
            url=candidate.url,
            provider=self.provider_name,
            raw_title=raw_title,
            raw_brand=brand_name,
            raw_price_str=None,
            raw_currency="INR",
            raw_images=[],
            raw_specs={"extraction_source": "html_markup"},
            extraction_method="html",
            extraction_time_ms=elapsed_ms,
            confidence=candidate.confidence,
            metadata={"domain": candidate.domain},
        )
