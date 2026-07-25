from fastapi import APIRouter, HTTPException

from backend.exceptions import (
    CounterGuardError,
    InvalidListingError,
    MarketplaceNotSupportedError,
    ParsingError,
    ScrapingConnectionError,
    ScrapingTimeoutError,
)
from backend.schemas.investigation import InvestigationReport, InvestigationRequest
from backend.services.investigation_service import InvestigationService

router = APIRouter()
investigation_service = InvestigationService()


@router.post(
    "/investigate",
    response_model=InvestigationReport,
    responses={
        200: {
            "description": "Investigation successfully completed and report generated."
        },
        400: {"description": "Invalid URL or Unsupported Marketplace."},
        502: {"description": "Upstream error scraping the target listing."},
        500: {"description": "Internal server error during investigation."},
    },
)
def investigate_listing(request: InvestigationRequest):
    """
    Endpoint to start an investigation using the Core Investigation Engine.

    This endpoint takes a product listing URL, synchronously fetches and parses the HTML,
    evaluates it using the multi-agent assessment system, and returns a structured InvestigationReport.
    """
    try:
        report = investigation_service.run_investigation(request)
        return report
    except (InvalidListingError, MarketplaceNotSupportedError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (ScrapingTimeoutError, ScrapingConnectionError, ParsingError) as e:
        raise HTTPException(status_code=502, detail=f"Upstream Error: {e}")
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
