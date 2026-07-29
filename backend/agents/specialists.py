import logging
from typing import Any

from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.collaboration.models.context import (
    AgentObservation,
    InvestigationContext,
)
from backend.prompts.specialist_prompts import (
    BRAND_SYSTEM_PROMPT,
    PRICE_SYSTEM_PROMPT,
    REVIEW_SYSTEM_PROMPT,
    SELLER_SYSTEM_PROMPT,
    build_specialist_user_prompt,
)
from backend.schemas.llm_models import (
    BrandAnalysisResult,
    PriceAnalysisResult,
    ReviewAnalysisResult,
    SellerAnalysisResult,
)
from backend.services.llm_service import LLMService, LLMServiceError
from backend.state import InvestigationState
from backend.tools.base import BaseTool
from backend.tools.live_tools import (
    ImageInput,
    PriceInput,
    ReputationInput,
    TrademarkInput,
    WhoisInput,
)

logger = logging.getLogger(__name__)


class BaseSpecialistAgent(BaseAgent):
    """
    Base class for specialist agents that process tool outputs and write observations into the Collaborative Blackboard.
    """

    def __init__(self, tools: list[BaseTool] = None):
        super().__init__()
        self.tools = tools or []
        self.llm_service = LLMService()
        self.system_prompt = ""
        self.response_model = None

    def answer_query(self, question: str, state: InvestigationState) -> str:
        return f"{self.__class__.__name__}: Active specialist."

    def run(self, state: InvestigationState) -> dict:
        logger.info(f"Executing {self.__class__.__name__} specialist pipeline.")

        tool_data_for_prompt, state_updates = self._execute_tools(state)

        listing_data = (
            state.get("scraping_result").listing.model_dump(mode="json")
            if state.get("scraping_result") and state["scraping_result"].listing
            else {}
        )

        evidence_data = (
            state.get("evidence").structured_evidence if state.get("evidence") else {}
        )

        graphrag_markdown = (
            state.get("context").graphrag_context if state.get("context") else None
        )

        user_prompt = build_specialist_user_prompt(
            listing_data=listing_data,
            evidence_data=evidence_data,
            tool_data=tool_data_for_prompt,
            graphrag_context=graphrag_markdown,
        )

        try:
            result = self.llm_service.generate_structured_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                response_model=self.response_model,
            )
            llm_updates = self._update_state(state, result)
            return {**state_updates, **llm_updates}
        except LLMServiceError as e:
            logger.error(f"{self.__class__.__name__} failed: {e}")
            llm_updates = self._update_state(state, self._get_fallback())
            return {**state_updates, **llm_updates}

    def _execute_tools(self, state: InvestigationState) -> tuple[dict | None, dict]:
        """Returns (tool_data_for_prompt_dict, state_update_dict)"""
        if not self.tools:
            return None, {}

        tool_outputs = {}
        all_state_updates = {}

        for tool in self.tools:
            try:
                input_data = self._prepare_tool_input(tool.name, state)
                if input_data:
                    logger.info(
                        f"Executing tool {tool.name} in {self.__class__.__name__}"
                    )
                    result = tool.execute(input_data)
                    tool_outputs[tool.name] = result.model_dump()
                    all_state_updates.update(
                        self._map_tool_result_to_state(tool.name, result)
                    )
            except Exception as e:
                logger.warning(f"Tool {tool.name} failed: {e}. Degrading gracefully.")

        if not tool_outputs:
            return None, {}

        return tool_outputs, all_state_updates

    def _prepare_tool_input(self, tool_name: str, state: InvestigationState) -> Any:
        return None

    def _map_tool_result_to_state(self, tool_name: str, result: Any) -> dict:
        return {}

    def _update_state(self, state: InvestigationState, result) -> dict:
        raise NotImplementedError

    def _get_fallback(self):
        raise NotImplementedError


@AgentRegistry.register("PriceAgent")
class PriceAgent(BaseSpecialistAgent):
    def __init__(self, tools: list[BaseTool] = None):
        super().__init__(tools)
        self.system_prompt = PRICE_SYSTEM_PROMPT
        self.response_model = PriceAnalysisResult

    def _prepare_tool_input(self, tool_name: str, state: InvestigationState) -> Any:
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        title = listing.title if listing and listing.title else "Unknown Product"

        if tool_name == "price_history":
            return PriceInput(product_name=title)
        return None

    def _map_tool_result_to_state(self, tool_name: str, result: Any) -> dict:
        if tool_name == "price_history":
            return {"price_history": result}
        return {}

    def _update_state(
        self, state: InvestigationState, result: PriceAnalysisResult
    ) -> dict:
        new_context = InvestigationContext(investigation_id="temp")
        new_context.shared_observations.append(
            AgentObservation(
                source_agent="PriceAgent",
                content=f"Risk Score: {result.risk_score}. Reasoning: {result.reasoning}",
                metadata={
                    "anomaly_detected": getattr(result, "anomaly_detected", False)
                },
            )
        )
        return {"price_analysis": result, "context": new_context}

    def _get_fallback(self) -> PriceAnalysisResult:
        return PriceAnalysisResult(
            anomaly_detected=False, reasoning="Service unavailable", risk_score=50
        )


@AgentRegistry.register("SellerAgent")
class SellerAgent(BaseSpecialistAgent):
    def __init__(self, tools: list[BaseTool] = None):
        super().__init__(tools)
        self.system_prompt = SELLER_SYSTEM_PROMPT
        self.response_model = SellerAnalysisResult

    def _prepare_tool_input(self, tool_name: str, state: InvestigationState) -> Any:
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        seller = (
            listing.seller_name
            if listing and listing.seller_name
            else "UnknownSeller.com"
        )
        req = state.get("request")
        req_url = req.listing_url if req and hasattr(req, "listing_url") else ""

        if tool_name == "whois_lookup":
            if req_url.startswith("demo://") or (
                listing
                and getattr(listing, "data_source", None) == "fallback_demo_data"
            ):
                return None
            if not seller or "." not in seller:
                return None
            return WhoisInput(domain=seller)
        elif tool_name == "seller_reputation":
            return ReputationInput(seller_name=seller)
        return None

    def _map_tool_result_to_state(self, tool_name: str, result: Any) -> dict:
        if tool_name == "whois_lookup":
            return {"whois_data": result}
        elif tool_name == "seller_reputation":
            return {"reputation_data": result}
        return {}

    def _update_state(
        self, state: InvestigationState, result: SellerAnalysisResult
    ) -> dict:
        new_context = InvestigationContext(investigation_id="temp")
        new_context.shared_observations.append(
            AgentObservation(
                source_agent="SellerAgent",
                content=f"Risk Score: {result.risk_score}. Reasoning: {result.reasoning}",
                metadata={
                    "reputation_risk": getattr(result, "reputation_risk", "Medium")
                },
            )
        )
        return {"seller_analysis": result, "context": new_context}

    def _get_fallback(self) -> SellerAnalysisResult:
        return SellerAnalysisResult(
            reputation_risk="Medium", reasoning="Service unavailable", risk_score=50
        )


@AgentRegistry.register("BrandAgent")
class BrandAgent(BaseSpecialistAgent):
    def __init__(self, tools: list[BaseTool] = None):
        super().__init__(tools)
        self.system_prompt = BRAND_SYSTEM_PROMPT
        self.response_model = BrandAnalysisResult

    def _prepare_tool_input(self, tool_name: str, state: InvestigationState) -> Any:
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        brand = listing.brand if listing and listing.brand else "GenericBrand"

        if tool_name == "trademark_lookup":
            return TrademarkInput(brand_name=brand)
        return None

    def _map_tool_result_to_state(self, tool_name: str, result: Any) -> dict:
        if tool_name == "trademark_lookup":
            return {"trademark_data": result}
        return {}

    def _update_state(
        self, state: InvestigationState, result: BrandAnalysisResult
    ) -> dict:
        new_context = InvestigationContext(investigation_id="temp")
        new_context.shared_observations.append(
            AgentObservation(
                source_agent="BrandAgent",
                content=f"Risk Score: {result.risk_score}. Reasoning: {result.reasoning}",
                metadata={
                    "authenticity_flags": getattr(result, "authenticity_flags", [])
                },
            )
        )
        return {"brand_analysis": result, "context": new_context}

    def _get_fallback(self) -> BrandAnalysisResult:
        return BrandAnalysisResult(
            authenticity_flags=[],
            reasoning="Service unavailable",
            risk_score=50,
        )


@AgentRegistry.register("ReviewAgent")
class ReviewAgent(BaseSpecialistAgent):
    def __init__(self, tools: list[BaseTool] = None):
        super().__init__(tools)
        self.system_prompt = REVIEW_SYSTEM_PROMPT
        self.response_model = ReviewAnalysisResult

    def _prepare_tool_input(self, tool_name: str, state: InvestigationState) -> Any:
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        img_url = (
            listing.image_url
            if listing and listing.image_url
            else "https://example.com/image.jpg"
        )

        if tool_name == "reverse_image_search":
            return ImageInput(image_url=img_url)
        return None

    def _map_tool_result_to_state(self, tool_name: str, result: Any) -> dict:
        if tool_name == "reverse_image_search":
            return {"reverse_image_data": result}
        return {}

    def _update_state(
        self, state: InvestigationState, result: ReviewAnalysisResult
    ) -> dict:
        new_context = InvestigationContext(investigation_id="temp")
        new_context.shared_observations.append(
            AgentObservation(
                source_agent="ReviewAgent",
                content=f"Risk Score: {result.risk_score}. Reasoning: {result.reasoning}",
                metadata={
                    "fake_reviews_detected": getattr(
                        result, "fake_reviews_detected", False
                    )
                },
            )
        )
        return {"review_analysis": result, "context": new_context}

    def _get_fallback(self) -> ReviewAnalysisResult:
        return ReviewAnalysisResult(
            fake_reviews_detected=False,
            reasoning="Service unavailable",
            risk_score=50,
        )
