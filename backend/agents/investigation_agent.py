import logging

from backend.prompts.investigation_prompt import (
    INVESTIGATION_SYSTEM_PROMPT,
    build_investigation_user_prompt,
)
from backend.schemas.investigation import AnalyzerResult, EvidenceResult
from backend.schemas.llm_models import AIInvestigationResult
from backend.schemas.scraping import ScrapingResult
from backend.services.llm_service import LLMService, LLMServiceError

logger = logging.getLogger(__name__)


class InvestigationAgent:
    def __init__(self):
        self.llm_service = LLMService()

    def investigate(
        self,
        scraping_result: ScrapingResult,
        analysis: AnalyzerResult,
        evidence: EvidenceResult,
    ) -> AIInvestigationResult:
        """
        Synthesizes the output of the deterministic pipeline into a comprehensive AI reasoning payload.
        """
        logger.info("Starting AI investigation layer.")

        listing_data = (
            scraping_result.listing.model_dump() if scraping_result.listing else {}
        )
        analyzer_data = analysis.model_dump()
        evidence_data = evidence.model_dump()

        user_prompt = build_investigation_user_prompt(
            listing_data, analyzer_data, evidence_data
        )

        try:
            result = self.llm_service.generate_investigation_result(
                system_prompt=INVESTIGATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            return result
        except LLMServiceError as e:
            logger.error(f"AI investigation failed, returning fallback. Error: {e}")
            # Graceful degradation: return a fallback result so the deterministic engine can still complete
            return AIInvestigationResult(
                summary="AI analysis unavailable due to service error.",
                detailed_reasoning="The AI reasoning service failed to respond or encountered an error.",
                suspicious_indicators=[],
                confidence_score=50.0,
            )
