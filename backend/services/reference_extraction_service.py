import logging
from typing import Optional, Tuple

from backend.schemas.canonical_product import CanonicalProductKnowledge
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.official_product import OfficialProductProfile
from backend.schemas.raw_extraction import RawExtractionResult
from backend.services.canonical_knowledge_builder import CanonicalKnowledgeBuilder
from backend.services.extraction_orchestrator import ExtractionOrchestrator

logger = logging.getLogger(__name__)


class ReferenceExtractionService:
    """
    ReferenceExtractionService (Sprint 17 Service Interface)

    Delegates extraction strategy selection, fallback cascades, provider fusion, and validation
    to `ExtractionOrchestrator`, and builds unified `CanonicalProductKnowledge` objects for AI agents via `CanonicalKnowledgeBuilder`.

    Architecture Flow:
      ReferenceExtractionService
              ↓
      ExtractionOrchestrator (Cascade & Fusion)
              ↓
      RawExtractionResult -> Normalization -> Validation -> OfficialProductProfile
              ↓
      CanonicalKnowledgeBuilder
              ↓
      CanonicalProductKnowledge (Consumed by Specialist AI Agents)
    """

    def __init__(
        self,
        orchestrator: Optional[ExtractionOrchestrator] = None,
        knowledge_builder: Optional[CanonicalKnowledgeBuilder] = None,
    ):
        self.orchestrator = orchestrator or ExtractionOrchestrator()
        self.knowledge_builder = knowledge_builder or CanonicalKnowledgeBuilder()
        logger.info(
            "[ReferenceExtractionService] Initialized with ExtractionOrchestrator and CanonicalKnowledgeBuilder."
        )

    def extract_profile(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[RawExtractionResult, OfficialProductProfile, bool]:
        """
        Extracts raw result and normalized profile baseline via ExtractionOrchestrator.
        """
        return self.orchestrator.execute_extraction_cascade(
            candidate=candidate, raw_content=raw_content
        )

    def extract_canonical_knowledge(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[CanonicalProductKnowledge, bool]:
        """
        Primary entry point: Executes extraction cascade and compiles unified CanonicalProductKnowledge
        for downstream AI specialist agents (BrandAgent, PriceAgent, VisionAgent, MetadataAgent).
        """
        _, profile, is_valid = self.extract_profile(candidate, raw_content)
        canonical_knowledge = self.knowledge_builder.build_from_profile(profile)
        return canonical_knowledge, is_valid
