import logging

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

    def run(self, state: InvestigationState) -> InvestigationState:
        logger.info("Running CoordinatorAgent to synthesize specialist findings.")

        specialist_results = {
            "price_analysis": state.get("price_analysis", {}),
            "seller_analysis": state.get("seller_analysis", {}),
            "brand_analysis": state.get("brand_analysis", {}),
            "review_analysis": state.get("review_analysis", {}),
        }

        # Convert Pydantic models to dicts for JSON serialization
        formatted_results = {
            k: v.model_dump() if hasattr(v, "model_dump") else v
            for k, v in specialist_results.items()
        }

        user_prompt = build_coordinator_user_prompt(formatted_results)

        try:
            result = self.llm_service.generate_structured_response(
                system_prompt=COORDINATOR_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=AIInvestigationResult,
            )
            state["coordinator_result"] = result
        except LLMServiceError as e:
            logger.error(f"CoordinatorAgent failed: {e}")
            state["coordinator_result"] = AIInvestigationResult(
                summary="AI analysis unavailable due to coordinator error.",
                detailed_reasoning="The coordinator service failed to respond.",
                suspicious_indicators=[],
                confidence_score=50.0,
            )

        return state
