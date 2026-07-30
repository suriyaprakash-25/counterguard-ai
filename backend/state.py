import operator
from typing import Annotated, Any, Dict, List, TypedDict

from backend.collaboration.models.context import AgentWorkspace, InvestigationContext
from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationReport,
    InvestigationRequest,
    RiskAssessment,
)
from backend.schemas.llm_models import AIInvestigationResult, PlanningResult
from backend.schemas.recommendation import TrustedProductResult
from backend.schemas.scraping import ScrapingResult


def merge_context(  # noqa: C901
    a: InvestigationContext, b: InvestigationContext
) -> InvestigationContext:
    if not a:
        return b
    if not b:
        return a

    merged = a.model_copy()

    if b.product_info:
        merged.product_info = {**a.product_info, **b.product_info}
    if b.seller_info:
        merged.seller_info = {**a.seller_info, **b.seller_info}
    if b.extracted_metadata:
        merged.extracted_metadata = {**a.extracted_metadata, **b.extracted_metadata}
    if b.marketplace and b.marketplace != "Global":
        merged.marketplace = b.marketplace

    existing_evidence_ids = {e.evidence_id for e in a.shared_evidence}
    for e in b.shared_evidence:
        if e.evidence_id not in existing_evidence_ids:
            merged.shared_evidence.append(e)
            existing_evidence_ids.add(e.evidence_id)

    existing_obs_ids = {o.id for o in a.shared_observations}
    for o in b.shared_observations:
        if o.id not in existing_obs_ids:
            merged.shared_observations.append(o)
            existing_obs_ids.add(o.id)

    merged.unresolved_questions.extend(
        [q for q in b.unresolved_questions if q not in a.unresolved_questions]
    )
    merged.tasks.extend([t for t in b.tasks if t not in a.tasks])

    def _get_step_key(s):
        ag = getattr(
            s,
            "agent",
            getattr(
                s, "agent_name", s.get("agent_name") if isinstance(s, dict) else ""
            ),
        )
        rs = getattr(
            s,
            "reason",
            getattr(s, "reasoning", s.get("reasoning") if isinstance(s, dict) else ""),
        )
        return (ag, rs)

    existing_steps = {_get_step_key(s) for s in a.confidence_timeline}
    for step in b.confidence_timeline:
        key = _get_step_key(step)
        if key not in existing_steps:
            merged.confidence_timeline.append(step)
            existing_steps.add(key)

    merged.recalculate_intermediate_risk()

    if b.graphrag_intelligence:
        merged.graphrag_intelligence = b.graphrag_intelligence
    if b.graphrag_context:
        merged.graphrag_context = b.graphrag_context
    if b.final_verdict:
        merged.final_verdict = b.final_verdict

    return merged


def merge_dict(a: dict, b: dict) -> dict:
    if not a:
        return b or {}
    if not b:
        return a or {}
    res = a.copy()
    res.update(b)
    return res


class InvestigationState(TypedDict, total=False):
    """
    Shared state containing the legacy pipeline outputs and the new Collaborative Blackboard.
    Annotated with proper list/dict reducers so parallel fan-out nodes accumulate state without overwriting.
    """

    request: InvestigationRequest
    scraping_result: ScrapingResult
    analysis: AnalyzerResult
    evidence: EvidenceResult
    risk: RiskAssessment
    planning_result: PlanningResult

    # -- SPRINT 14: AUTOMATION --
    from backend.automation.models.domain import InvestigationPlan

    investigation_plan: InvestigationPlan

    # -- SPRINT 12: COLLABORATIVE BLACKBOARD --
    context: Annotated[InvestigationContext, merge_context]
    workspaces: Dict[str, AgentWorkspace]  # Maps agent name to their workspace

    # Parallel Specialist State Accumulators (Proper Reducers)
    visual_similarity: float
    visual_findings: Annotated[List[str], operator.add]
    specialist_findings: Annotated[List[str], operator.add]
    specialist_evidence: Annotated[Dict[str, Any], merge_dict]

    # Explanations
    explanation: str

    # Trusted Product Recommendation Agent
    trusted_product_result: TrustedProductResult
    recommended_products: List[Dict[str, Any]]

    # -- SPRINT 17: REFERENCE DISCOVERY ARCHITECTURE FOUNDATION --
    from backend.schemas.official_product import OfficialProductProfile

    official_product_profile: OfficialProductProfile
    reference_discovery_result: Dict[str, Any]
    reference_status: str
    reference_source: str
    reference_confidence: float

    # Legacy Outputs
    coordinator_result: AIInvestigationResult
    report: InvestigationReport
    status: str
    error: str
