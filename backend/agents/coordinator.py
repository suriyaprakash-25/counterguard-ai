import logging

from backend.collaboration.models.context import InvestigationContext
from backend.collaboration.services.consensus import ConsensusService
from backend.collaboration.services.explainability import ExplainabilityService
from backend.collaboration.services.validation import ValidationService
from backend.prompts.specialist_prompts import (
    COORDINATOR_SYSTEM_PROMPT,
    build_coordinator_user_prompt,
)
from backend.schemas.llm_models import AIInvestigationResult
from backend.services.llm_service import LLMService, LLMServiceError
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.validation_service = ValidationService()
        self.consensus_service = ConsensusService()
        self.explainability_service = ExplainabilityService()

    def run(self, state: InvestigationState) -> dict:
        logger.info("Running CoordinatorAgent to synthesize Blackboard context.")

        context: InvestigationContext = state.get("context")
        if not context:
            logger.warning("No InvestigationContext found. Creating empty context.")
            context = InvestigationContext(investigation_id="temp")

        # 1. Validate Evidence
        self.validation_service.validate_evidence(context)

        # 2. Resolve Conflicts
        conflicts = self.consensus_service.resolve_conflicts(context)

        # 3. Calculate Final Confidence
        final_confidence = self.consensus_service.calculate_consensus_confidence(
            context
        )

        # 4. Generate Explainability Report
        explanation = self.explainability_service.generate_explanation(
            context, final_confidence
        )

        # Format Blackboard data for the LLM
        formatted_results = {
            "evidence": [e.model_dump(mode="json") for e in context.shared_evidence],
            "observations": [
                o.model_dump(mode="json") for o in context.shared_observations
            ],
            "conflicts": conflicts,
            "final_confidence": final_confidence,
            "graphrag_context": context.graphrag_context,
        }

        user_prompt = build_coordinator_user_prompt(formatted_results)

        try:
            result = self.llm_service.generate_structured_response(
                system_prompt=COORDINATOR_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=AIInvestigationResult,
            )
            # Override LLM confidence with computed Consensus confidence
            result.confidence_score = final_confidence

            return {
                "coordinator_result": result,
                "context": context,
                "explanation": explanation,
            }
        except LLMServiceError as e:
            logger.error(f"CoordinatorAgent failed: {e}")
            fallback = AIInvestigationResult(
                summary="AI Synthesis failed due to service error.",
                detailed_reasoning="Unable to reach LLM service.",
                suspicious_indicators=[],
                confidence_score=0.0,
            )
            return {
                "coordinator_result": fallback,
                "context": context,
                "explanation": explanation,
            }
