import logging

from backend.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    build_planner_user_prompt,
)
from backend.schemas.llm_models import PlanningResult
from backend.services.llm_service import LLMService, LLMServiceError
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


class PlanningAgent:
    def __init__(self):
        self.llm_service = LLMService()

    def run(self, state: InvestigationState) -> dict:
        logger.info("Running PlanningAgent to determine investigation strategy.")

        listing_data = (
            state.get("scraping_result").listing.model_dump()
            if state.get("scraping_result") and state["scraping_result"].listing
            else {}
        )
        analyzer_data = (
            state.get("analysis").model_dump() if state.get("analysis") else {}
        )
        evidence_data = (
            state.get("evidence").model_dump() if state.get("evidence") else {}
        )

        user_prompt = build_planner_user_prompt(
            listing_data, analyzer_data, evidence_data
        )

        try:
            result = self.llm_service.generate_structured_response(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=PlanningResult,
            )
            logger.info(f"Planned Specialists: {result.selected_specialists}")
            return {"planning_result": result}
        except LLMServiceError as e:
            logger.error(f"PlanningAgent failed: {e}")
            # Fallback plan: run all specialists to be safe
            fallback = PlanningResult(
                selected_specialists=[
                    "PriceAgent",
                    "SellerAgent",
                    "BrandAgent",
                    "ReviewAgent",
                ],
                priority="High",
                execution_strategy="Fallback plan: executing all specialists due to LLM error.",
                rationale="Planner service was unavailable.",
            )
            return {"planning_result": fallback}
