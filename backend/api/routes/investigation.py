"""
Investigation API route definitions.
Thin routing layer that delegates core operational logic to domain services.
"""

from fastapi import APIRouter

from backend.api.schemas.investigation_request import InvestigationRequest
from backend.api.schemas.investigation_response import InvestigationResponse
from backend.services.mock_investigation_service import (
    generate_mock_investigation,
)
from backend.state import InvestigationState

router = APIRouter()


@router.post("/investigate", response_model=InvestigationResponse)
async def investigate(request: InvestigationRequest) -> InvestigationState:
    """
    Start an automated investigation for a target listing and return canonical state.

    Args:
        request: Validated payload containing listing URL and marketplace.
    """
    return generate_mock_investigation(request.listing_url, request.marketplace)
