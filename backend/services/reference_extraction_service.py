import logging
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


class ReferenceExtractionService:
    """
    ReferenceExtractionService (Sprint 17 Phase 3 Foundation)

    Orchestrates the extraction pipeline flow:
      Verified Source (SourceCandidate)
              ↓
      ExtractionProvider Selection & Execution (Strategy Architecture)
              ↓
      RawExtractionResult (Un-normalized Intermediate Model)
              ↓
      ExtractionNormalizationEngine (Canonical Unit & String Normalization)
              ↓
      ExtractionValidationEngine (Quality Threshold Check)
              ↓
      OfficialProductProfile
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
            f"[ReferenceExtractionService] Initialized with {len(self.providers)} extraction providers."
        )

    def select_provider(self, candidate: SourceCandidate) -> ExtractionProvider:
        """Selects the first matching extraction strategy provider for a given SourceCandidate."""
        for provider in self.providers:
            if provider.supports(candidate):
                return provider
        return self.providers[-1]  # Default fallback to HTMLExtractionProvider

    def extract_profile(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[RawExtractionResult, OfficialProductProfile, bool]:
        """
        Primary extraction entry point executing the full extraction pipeline.
        Returns Tuple[RawExtractionResult, OfficialProductProfile, is_valid: bool].
        """
        logger.debug(
            f"[ReferenceExtractionService] Starting extraction for candidate '{candidate.url}'."
        )

        # STAGE 1: Strategy Provider Selection & Execution
        provider = self.select_provider(candidate)
        raw_result = provider.extract(candidate=candidate, raw_content=raw_content)

        # STAGE 2: Normalization
        normalized_profile = self.normalization_engine.normalize(raw_result)

        # STAGE 3: Validation
        is_valid, reason = self.validation_engine.validate(normalized_profile)
        normalized_profile.metadata["validation_reason"] = reason

        return raw_result, normalized_profile, is_valid
