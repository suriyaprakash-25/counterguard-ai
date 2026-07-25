from fastapi import APIRouter, HTTPException

from backend.schemas.investigation import InvestigationReport, InvestigationRequest
from backend.services.investigation_service import InvestigationService

router = APIRouter()
investigation_service = InvestigationService()


@router.post("/investigate", response_model=InvestigationReport)
async def investigate(request: InvestigationRequest):
    """
    Endpoint to start an investigation using the Core Investigation Engine.
    """
    try:
        report = investigation_service.run_investigation(request)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
