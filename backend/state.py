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


def merge_context(
    a: InvestigationContext, b: InvestigationContext
) -> InvestigationContext:
    if not a:
        return b
    if not b:
        return a

    # Create a new instance to avoid mutating the original
    merged = a.model_copy()

    # Safely merge lists avoiding duplicates by ID if possible, otherwise extend
    merged.shared_evidence.extend(
        [e for e in b.shared_evidence if e not in a.shared_evidence]
    )
    merged.shared_observations.extend(
        [o for o in b.shared_observations if o not in a.shared_observations]
    )
    merged.unresolved_questions.extend(
        [q for q in b.unresolved_questions if q not in a.unresolved_questions]
    )
    merged.tasks.extend([t for t in b.tasks if t not in a.tasks])
    merged.confidence_timeline.extend(b.confidence_timeline)

    # Merge GraphRAG Intelligence
    if b.graphrag_intelligence:
        merged.graphrag_intelligence = b.graphrag_intelligence
    if b.graphrag_context:
        merged.graphrag_context = b.graphrag_context

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

    # Legacy Outputs
    coordinator_result: AIInvestigationResult
    report: InvestigationReport
    status: str
    error: str
