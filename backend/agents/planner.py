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

            # Initialize InvestigationContext Blackboard
            listing_obj = (
                state.get("scraping_result").listing
                if state.get("scraping_result")
                else None
            )
            product_info = {
                "title": listing_obj.title if listing_obj else "Unknown Product",
                "price": listing_obj.price if listing_obj else 0.0,
                "brand": listing_obj.brand if listing_obj else "",
                "image_url": listing_obj.image_url if listing_obj else "",
            }
            marketplace = (
                listing_obj.marketplace
                if listing_obj
                and hasattr(listing_obj, "marketplace")
                and listing_obj.marketplace
                else "Global"
            )
            seller_info = {
                "name": listing_obj.seller_name if listing_obj else "Unknown Seller"
            }

            from backend.collaboration.models.context import InvestigationContext
            from backend.collaboration.models.protocol import AgentObservation
            from backend.memory.models.domain import Evidence

            new_context = InvestigationContext(
                product_info=product_info,
                marketplace=marketplace,
                seller_info=seller_info,
                extracted_metadata=listing_data.get("metadata", {}),
            )
            plan_ev = Evidence(
                agent_name="PlanningAgent",
                source_agent="PlanningAgent",
                category="Strategy",
                title="Target Strategy Plan",
                description=f"Selected specialists: {', '.join(result.selected_specialists)}. Priority: {result.priority}",
                severity="info",
                confidence=0.95,
                source="investigation_planner",
                metadata={
                    "priority": result.priority,
                    "specialists": result.selected_specialists,
                },
            )
            new_context.add_evidence(plan_ev)
            new_context.add_observation(
                AgentObservation(
                    source_agent="PlanningAgent",
                    content=f"Strategy: {result.execution_strategy}. Rationale: {result.rationale}",
                )
            )

            return {"planning_result": result, "context": new_context}
        except LLMServiceError as e:
            logger.error(f"PlanningAgent failed: {e}")
            fallback = PlanningResult(
                selected_specialists=[
                    "PriceAgent",
                    "SellerAgent",
                    "BrandAgent",
                    "ReviewAgent",
                    "BrandIntelligenceAgent",
                    "SpecificationValidationAgent",
                    "AuthorizedSellerAgent",
                    "MetadataIntelligenceAgent",
                ],
                priority="High",
                execution_strategy="Fallback plan: executing all specialists due to LLM error.",
                rationale="Planner service was unavailable.",
            )

            from backend.collaboration.models.context import InvestigationContext
            from backend.memory.models.domain import Evidence

            new_context = InvestigationContext()
            plan_ev = Evidence(
                agent_name="PlanningAgent",
                source_agent="PlanningAgent",
                category="Strategy",
                title="Fallback Strategy Plan",
                description="Executing all specialists due to service unavailability.",
                severity="medium",
                confidence=0.5,
                source="investigation_planner",
            )
            new_context.add_evidence(plan_ev)
            return {"planning_result": fallback, "context": new_context}
