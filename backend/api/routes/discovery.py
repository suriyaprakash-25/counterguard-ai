import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status

from backend.discovery.parallel_launcher import ParallelInvestigationLauncher
from backend.discovery.service import DiscoveryService
from backend.schemas.discovery import DiscoverySearchRequest, DiscoverySearchResponse
from backend.schemas.parallel_launch import (
    BatchStatusResponse,
    ParallelLaunchRequest,
    ParallelLaunchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/discovery", tags=["Discovery"])
discovery_service = DiscoveryService()
launcher = ParallelInvestigationLauncher()


@router.post(
    "/search",
    response_model=DiscoverySearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Product Candidate Search across Marketplaces",
    description="Discovers candidate product listings across supported marketplaces (Amazon, Flipkart, Meesho, TradeIndia, AJIO, Myntra) without triggering investigation.",
)
async def search_product_candidates(
    request: DiscoverySearchRequest
) -> DiscoverySearchResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query string cannot be empty.",
        )

    try:
        response = await discovery_service.discover_products(request)
        return response
    except Exception as e:
        logger.error(
            f"Product candidate search failed for query '{request.query}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product candidate discovery failed: {str(e)}",
        )


@router.get(
    "/marketplaces",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List Supported Discovery Marketplaces",
    description="Returns the list of marketplaces currently integrated with the Product Search & Discovery subsystem.",
)
async def get_supported_marketplaces() -> Dict[str, Any]:
    marketplaces = discovery_service.router.get_supported_marketplaces()
    return {"supported_marketplaces": marketplaces, "count": len(marketplaces)}


# ── Sprint 2.3: Parallel Investigation Launcher ───────────────────────────────


@router.post(
    "/launch",
    response_model=ParallelLaunchResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Launch Parallel Investigations from Discovery Candidates",
    description=(
        "Accepts 1–10 selected listing candidates from a discovery search result and "
        "launches concurrent LangGraph investigations for each. "
        "Returns a batch receipt with investigation IDs and a batch_id for status polling. "
        "Does NOT block — investigations run asynchronously in background threads."
    ),
)
def launch_parallel_investigations(
    request: ParallelLaunchRequest
) -> ParallelLaunchResponse:
    if not request.candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one candidate must be provided.",
        )
    if len(request.candidates) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 candidates can be launched in a single batch.",
        )

    try:
        response = launcher.launch(request)
        logger.info(
            f"Parallel batch '{response.batch_id}' launched: "
            f"{response.total_launched} investigation(s)"
        )
        return response
    except Exception as e:
        logger.error(f"Parallel launch failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to launch investigations: {str(e)}",
        )


@router.get(
    "/{candidate_id}/lineage",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get ListingCandidate Lineage Graph & Provenance",
    description="Returns step-by-step cryptographic lineage, archive IDs, hashes, and DAG graph nodes for a specific ListingCandidate.",
)
def get_candidate_lineage_api(candidate_id: str) -> Dict[str, Any]:
    from backend.services.evidence_lineage_service import evidence_lineage_service

    return evidence_lineage_service.get_candidate_lineage(candidate_id)


@router.get(
    "/launch/{batch_id}/status",
    response_model=BatchStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Poll Batch Investigation Status",
    description=(
        "Returns live status for all investigations in a batch launched via POST /discovery/launch. "
        "Poll this endpoint until is_complete=true."
    ),
)
def get_batch_status(batch_id: str) -> BatchStatusResponse:
    result = ParallelInvestigationLauncher.get_batch_status(batch_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch ID '{batch_id}' not found. Batch registry is in-memory and resets on server restart.",
        )
    return result


# ── Sprint 2.5: Product Intelligence Report ───────────────────────────────────

from backend.discovery.product_report_service import ProductReportService
from backend.schemas.product_report import (
    ProductIntelligenceReport,
    ProductIntelligenceReportRequest,
)

report_service = ProductReportService()


@router.post(
    "/report",
    response_model=ProductIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Generate Aggregated Product Intelligence Report",
    description=(
        "Accepts a list of completed investigation IDs and generates a synthesized "
        "Product Intelligence Report featuring overall product risk, safe/suspicious counts, "
        "highest risk marketplace, recommended seller, evidence summary, and coordinator summary."
    ),
)
def generate_product_report(
    request: ProductIntelligenceReportRequest
) -> ProductIntelligenceReport:
    if not request.investigation_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one investigation_id must be provided.",
        )
    try:
        report = report_service.generate_report(request)
        return report
    except Exception as e:
        logger.error(f"Failed to generate product report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate product report: {str(e)}",
        )


@router.get(
    "/batch/{batch_id}/report",
    response_model=ProductIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Generate Product Intelligence Report from Batch ID",
    description="Fetches investigation IDs from an active batch registry and generates a Product Intelligence Report.",
)
def generate_report_from_batch(batch_id: str) -> ProductIntelligenceReport:
    batch = ParallelInvestigationLauncher.get_batch_status(batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch ID '{batch_id}' not found.",
        )

    inv_ids = [j.investigation_id for j in batch.jobs]
    request = ProductIntelligenceReportRequest(
        investigation_ids=inv_ids,
        product_name=batch.jobs[0].title if batch.jobs else None,
    )
    return report_service.generate_report(request)
