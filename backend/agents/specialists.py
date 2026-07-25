import logging

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

logger = logging.getLogger(__name__)


class BaseSpecialistAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.system_prompt = ""
        self.response_model = None

    def run(self, state: InvestigationState) -> dict:
        logger.info(f"Running {self.__class__.__name__}")

        listing_data = (
            state.get("scraping_result").listing.model_dump()
            if state.get("scraping_result") and state["scraping_result"].listing
            else {}
        )
        evidence_data = (
            state.get("evidence").model_dump() if state.get("evidence") else {}
        )

        user_prompt = build_specialist_user_prompt(listing_data, evidence_data)

        try:
            result = self.llm_service.generate_structured_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                response_model=self.response_model,
            )
            return self._update_state(state, result)
        except LLMServiceError as e:
            logger.error(f"{self.__class__.__name__} failed: {e}")
            return self._update_state(state, self._get_fallback())

    def _update_state(self, state: InvestigationState, result) -> dict:
        raise NotImplementedError

    def _get_fallback(self):
        raise NotImplementedError


class PriceAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = PRICE_SYSTEM_PROMPT
        self.response_model = PriceAnalysisResult

    def _update_state(
        self, state: InvestigationState, result: PriceAnalysisResult
    ) -> dict:
        return {"price_analysis": result}

    def _get_fallback(self) -> PriceAnalysisResult:
        return PriceAnalysisResult(
            anomaly_detected=False, reasoning="Service unavailable", risk_score=50
        )


class SellerAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = SELLER_SYSTEM_PROMPT
        self.response_model = SellerAnalysisResult

    def _update_state(
        self, state: InvestigationState, result: SellerAnalysisResult
    ) -> dict:
        return {"seller_analysis": result}

    def _get_fallback(self) -> SellerAnalysisResult:
        return SellerAnalysisResult(
            reputation_risk="Unknown", reasoning="Service unavailable", risk_score=50
        )


class BrandAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = BRAND_SYSTEM_PROMPT
        self.response_model = BrandAnalysisResult

    def _update_state(
        self, state: InvestigationState, result: BrandAnalysisResult
    ) -> dict:
        return {"brand_analysis": result}

    def _get_fallback(self) -> BrandAnalysisResult:
        return BrandAnalysisResult(
            authenticity_flags=[], reasoning="Service unavailable", risk_score=50
        )


class ReviewAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__()
        self.system_prompt = REVIEW_SYSTEM_PROMPT
        self.response_model = ReviewAnalysisResult

    def _update_state(
        self, state: InvestigationState, result: ReviewAnalysisResult
    ) -> dict:
        return {"review_analysis": result}

    def _get_fallback(self) -> ReviewAnalysisResult:
        return ReviewAnalysisResult(
            fake_reviews_detected=False, reasoning="Service unavailable", risk_score=50
        )
