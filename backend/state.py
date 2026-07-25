from typing import TypedDict

from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationReport,
    InvestigationRequest,
    RiskAssessment,
)
from backend.schemas.llm_models import (
    AIInvestigationResult,
    BrandAnalysisResult,
    PriceAnalysisResult,
    ReviewAnalysisResult,
    SellerAnalysisResult,
)
from backend.schemas.scraping import ScrapingResult


class InvestigationState(TypedDict, total=False):
    """
    Shared state that doubles as the Evidence Timeline.
    This is the single source of truth for the investigation across the graph.
    """

    request: InvestigationRequest
    scraping_result: ScrapingResult
    analysis: AnalyzerResult
    evidence: EvidenceResult
    risk: RiskAssessment

    # Specialist outputs
    price_analysis: PriceAnalysisResult
    seller_analysis: SellerAnalysisResult
    brand_analysis: BrandAnalysisResult
    review_analysis: ReviewAnalysisResult

    # Final AI synthesis
    coordinator_result: AIInvestigationResult

    # Final combined report
    report: InvestigationReport

    # Legacy fields
    status: str
    error: str
