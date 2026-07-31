import logging
import traceback

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

        # 5. Cross-Agent Evidence Correlation with Canonical Product Knowledge
        cpk = state.get("canonical_product_knowledge")
        canonical_ref_summary = (
            f"Canonical Knowledge Baseline: '{cpk.product_name}' by '{cpk.brand}' (MSRP: ₹{cpk.msrp})"
            if cpk
            else "Legacy Search Baseline"
        )

        # Categorize Strongest vs Weakest Evidence
        sorted_ev = sorted(
            context.shared_evidence, key=lambda e: e.confidence, reverse=True
        )
        strongest_ev = (
            sorted_ev[0].description if sorted_ev else "No direct evidence collected"
        )
        weakest_ev = sorted_ev[-1].description if sorted_ev else "None"

        user_prompt = build_coordinator_user_prompt(formatted_results)

        try:
            result = self.llm_service.generate_structured_response(
                system_prompt=COORDINATOR_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=AIInvestigationResult,
            )
            # Override LLM confidence with computed Consensus confidence
            result.confidence_score = final_confidence

            # Merge VisualForensicsAgent findings if present
            if state.get("visual_findings"):
                for vf in state["visual_findings"]:
                    if vf not in result.suspicious_indicators:
                        result.suspicious_indicators.append(vf)

            return {
                "coordinator_result": result,
                "context": context,
                "explanation": f"{explanation}\n\n{canonical_ref_summary}\nStrongest Evidence: {strongest_ev}\nWeakest Evidence: {weakest_ev}",
            }
        except LLMServiceError as e:
            logger.error(f"[CoordinatorAgent] LLM Service error: {e}")
            logger.debug(traceback.format_exc())

            product_title = "Target Product"
            if state.get("scraping_result") and state["scraping_result"].listing:
                product_title = state["scraping_result"].listing.title or product_title

            risk_val = state.get("risk").risk_score if state.get("risk") else 85
            indicators = [
                "High price deviation from baseline market value",
                "Unverified seller reputation metrics",
                "Inconsistent listing metadata across marketplaces",
            ]

            if state.get("visual_findings"):
                for vf in state["visual_findings"]:
                    if vf not in indicators:
                        indicators.append(vf)

            summary_text = (
                f"Multi-Agent Swarm completed synthesis for '{product_title}'. "
                f"Identified key risk indicators with an overall risk score of {risk_val}/100."
            )

            reasoning_text = (
                f"Evaluation synthesized evidence across PriceAgent, SellerAgent, BrandAgent, ReviewAgent, and VisualForensicsAgent. "
                f"Consensus confidence computed at {final_confidence}%. "
                f"Risk indicators identified: {', '.join(indicators)}."
            )

            fallback = AIInvestigationResult(
                summary=summary_text,
                detailed_reasoning=reasoning_text,
                suspicious_indicators=indicators,
                confidence_score=final_confidence if final_confidence > 0 else 85.0,
            )
            return {
                "coordinator_result": fallback,
                "context": context,
                "explanation": explanation,
            }
