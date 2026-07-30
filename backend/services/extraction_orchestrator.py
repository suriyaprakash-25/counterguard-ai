import logging
import time
from typing import List, Optional, Tuple

from backend.providers.extraction.api_provider import StructuredApiExtractionProvider
from backend.providers.extraction.base_provider import ExtractionProvider
from backend.providers.extraction.html_provider import HTMLExtractionProvider
from backend.providers.extraction.jsonld_provider import JsonLdExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.official_product import OfficialProductProfile
from backend.schemas.raw_extraction import RawExtractionResult
from backend.services.extraction_normalization_engine import (
    ExtractionNormalizationEngine,
)
from backend.services.extraction_validation_engine import ExtractionValidationEngine

logger = logging.getLogger(__name__)


class ExtractionOrchestrator:
    """
    ExtractionOrchestrator (Sprint 17 Orchestration Layer)

    Decouples extraction provider selection, fallback cascades, provider fusion, retries,
    normalization, and validation away from ReferenceExtractionService.
    """

    def __init__(self, providers: Optional[List[ExtractionProvider]] = None):
        self.providers: List[ExtractionProvider] = providers or [
            JsonLdExtractionProvider(),
            StructuredApiExtractionProvider(),
            HTMLExtractionProvider(),  # Fallback strategy
        ]
        self.normalization_engine = ExtractionNormalizationEngine()
        self.validation_engine = ExtractionValidationEngine()
        logger.info(
            f"[ExtractionOrchestrator] Initialized with {len(self.providers)} providers."
        )

    def select_providers(self, candidate: SourceCandidate) -> List[ExtractionProvider]:
        """
        Returns an ordered list of candidate extraction strategy providers (Primary + Fallbacks).
        """
        matching = [p for p in self.providers if p.supports(candidate)]
        if not matching:
            return [self.providers[-1]]  # Default fallback to HTMLExtractionProvider
        return matching

    def execute_extraction_cascade(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[RawExtractionResult, OfficialProductProfile, bool]:
        """
        Executes provider strategy cascade (Primary -> Fallbacks) with confidence merging and validation.
        """
        start_time = time.time()
        active_providers = self.select_providers(candidate)

        best_raw: Optional[RawExtractionResult] = None
        best_profile: Optional[OfficialProductProfile] = None
        best_is_valid = False

        for provider in active_providers:
            try:
                raw_res = provider.extract(candidate=candidate, raw_content=raw_content)
                norm_profile = self.normalization_engine.normalize(raw_res)
                is_valid, reason = self.validation_engine.validate(norm_profile)
                norm_profile.metadata["validation_reason"] = reason

                if is_valid:
                    return raw_res, norm_profile, True

                if (
                    not best_profile
                    or norm_profile.confidence > best_profile.confidence
                ):
                    best_raw = raw_res
                    best_profile = norm_profile
                    best_is_valid = is_valid

            except Exception as err:
                logger.error(
                    f"[ExtractionOrchestrator] Provider '{provider.provider_name}' failed: {err}"
                )

        # If fallback exhausted, return best available profile
        if best_raw and best_profile:
            return best_raw, best_profile, best_is_valid

        # Empty fallback placeholder
        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        fallback_raw = RawExtractionResult(
            url=candidate.url,
            provider="FallbackOrchestrator",
            raw_title=candidate.title,
            extraction_time_ms=elapsed_ms,
            confidence=0.0,
        )
        fallback_profile = self.normalization_engine.normalize(fallback_raw)
        return fallback_raw, fallback_profile, False
