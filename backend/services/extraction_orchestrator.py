import logging
import time
from typing import List, Optional, Tuple

from backend.providers.extraction.api_provider import StructuredApiExtractionProvider
from backend.providers.extraction.base_provider import ExtractionProvider
from backend.providers.extraction.html_provider import HTMLExtractionProvider
from backend.providers.extraction.jsonld_provider import JsonLdExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence
from backend.schemas.official_product import OfficialProductProfile
from backend.schemas.raw_extraction import RawExtractionResult
from backend.services.extraction_normalization_engine import (
    ExtractionNormalizationEngine,
)
from backend.services.extraction_validation_engine import ExtractionValidationEngine

logger = logging.getLogger(__name__)


class ExtractionOrchestrator:
    """
    Production ExtractionOrchestrator (Sprint 17 Phase 3 Implementation)

    Orchestrates provider cascade, intelligent provider fusion, confidence merging, and validation.

    Cascade Priority:
      1. JsonLdExtractionProvider  (Highest structured schema confidence: 0.98)
      2. StructuredApiExtractionProvider (Next.js / Shopify state payload: 0.97)
      3. HTMLExtractionProvider   (DOM Field Extractors fallback: 0.90)

    Provider Fusion:
      Fuses findings across providers (e.g. JSON-LD title + HTML specs + API images) by taking
      highest-confidence values for every field into a unified composite result.
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
        """Returns ordered active extraction strategy providers."""
        active = [p for p in self.providers if p.supports(candidate)]
        if not active:
            return [self.providers[-1]]
        return active

    def fuse_extraction_results(  # noqa: C901
        self, results: List[RawExtractionResult]
    ) -> RawExtractionResult:
        """
        Fuses multiple RawExtractionResult objects taking highest-confidence fields.
        """
        if not results:
            raise ValueError("Cannot fuse empty extraction results list.")

        if len(results) == 1:
            return results[0]

        best_title: Optional[str] = None
        best_brand: Optional[str] = None
        best_price: Optional[str] = None
        best_currency: str = "INR"
        fused_images: List[str] = []
        fused_specs: dict = {}
        fused_evidence: List[ExtractionEvidence] = []
        max_confidence = 0.0

        for r in results:
            fused_evidence.extend(r.evidence_trail)
            if r.confidence > max_confidence:
                max_confidence = r.confidence

            if not best_title and r.raw_title:
                best_title = r.raw_title
            if not best_brand and r.raw_brand:
                best_brand = r.raw_brand
            if not best_price and r.raw_price_str:
                best_price = r.raw_price_str
                best_currency = r.raw_currency

            for img in r.raw_images:
                if img not in fused_images:
                    fused_images.append(img)

            for k, v in r.raw_specs.items():
                if k not in fused_specs:
                    fused_specs[k] = v

        primary = results[0]
        return RawExtractionResult(
            url=primary.url,
            provider=f"FusedOrchestrator({', '.join(r.provider for r in results)})",
            raw_title=best_title or primary.raw_title,
            raw_brand=best_brand or primary.raw_brand,
            raw_price_str=best_price or primary.raw_price_str,
            raw_currency=best_currency,
            raw_images=fused_images or primary.raw_images,
            raw_specs=fused_specs or primary.raw_specs,
            evidence_trail=fused_evidence,
            extraction_method="provider_fusion",
            extraction_time_ms=sum(r.extraction_time_ms for r in results),
            confidence=max_confidence,
            metadata={"fused_provider_count": len(results)},
        )

    def execute_extraction_cascade(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[RawExtractionResult, OfficialProductProfile, bool]:
        """
        Executes provider strategy cascade with intelligent provider fusion and validation.
        """
        start_time = time.time()
        active_providers = self.select_providers(candidate)
        collected_results: List[RawExtractionResult] = []

        for provider in active_providers:
            try:
                raw_res = provider.extract(candidate=candidate, raw_content=raw_content)
                collected_results.append(raw_res)
            except Exception as err:
                logger.error(
                    f"[ExtractionOrchestrator] Provider '{provider.provider_name}' failed: {err}"
                )

        if collected_results:
            fused_raw = self.fuse_extraction_results(collected_results)
            norm_profile = self.normalization_engine.normalize(fused_raw)
            is_valid, reason = self.validation_engine.validate(norm_profile)
            norm_profile.metadata["validation_reason"] = reason
            return fused_raw, norm_profile, is_valid

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
