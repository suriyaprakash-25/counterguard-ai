import logging
import time

from backend.providers.extraction.base_provider import ExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.raw_extraction import RawExtractionResult

logger = logging.getLogger(__name__)


class JsonLdExtractionProvider(ExtractionProvider):
    """
    JsonLdExtractionProvider (Strategy Provider)

    Extracts Schema.org / JSON-LD product microdata (used by Apple, Nike, etc.).
    """

    JSONLD_DOMAINS = {"apple.com", "nike.com", "adidas.com", "gucci.com", "ray-ban.com"}

    @property
    def provider_name(self) -> str:
        return "JsonLdExtractionProvider"

    def supports(self, candidate: SourceCandidate) -> bool:
        return (
            candidate.domain in self.JSONLD_DOMAINS or "json_ld" in candidate.metadata
        )

    def extract(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> RawExtractionResult:
        start_time = time.time()
        logger.debug(
            f"[{self.provider_name}] Extracting JSON-LD microdata from URL '{candidate.url}'."
        )

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

        return RawExtractionResult(
            url=candidate.url,
            provider=self.provider_name,
            raw_title=candidate.title,
            raw_brand=candidate.domain.split(".")[0].capitalize(),
            raw_specs={"microdata_format": "schema.org/Product"},
            extraction_method="json_ld",
            extraction_time_ms=elapsed_ms,
            confidence=0.95,
            metadata={"domain": candidate.domain},
        )
