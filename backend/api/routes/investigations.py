from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.database.repositories import (
    EvidenceRepository,
    InvestigationRepository,
    ReportRepository,
)
from backend.exceptions import CounterGuardError
from backend.schemas.history import (
    DeleteInvestigationResponse,
    InvestigationDetailResponse,
    InvestigationListResponse,
)
from backend.services.history_service import InvestigationHistoryService

router = APIRouter()


def get_history_service(
    session: Session = Depends(get_db_session),
) -> InvestigationHistoryService:
    """
    Dependency generator creating a configured InvestigationHistoryService with DB repositories.
    """
    inv_repo = InvestigationRepository(session)
    ev_repo = EvidenceRepository(session)
    rep_repo = ReportRepository(session)
    return InvestigationHistoryService(
        investigation_repo=inv_repo,
        evidence_repo=ev_repo,
        report_repo=rep_repo,
    )


@router.get(
    "/investigations",
    response_model=InvestigationListResponse,
    responses={
        200: {"description": "Successfully retrieved list of investigations."},
        500: {"description": "Internal server error during database query."},
    },
)
def get_investigation_history(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    marketplace: Optional[str] = Query(None, description="Filter by marketplace"),
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter by investigation status"
    ),
    sort_by: str = Query(
        "created_at", description="Field to sort by (created_at, status, marketplace)"
    ),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    service: InvestigationHistoryService = Depends(get_history_service),
) -> InvestigationListResponse:
    """
    Retrieve a paginated, filtered, and sorted list of completed or in-progress investigations.
    """
    try:
        return service.list_investigations(
            page=page,
            page_size=page_size,
            marketplace=marketplace,
            status=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.get(
    "/investigations/{id}",
    response_model=InvestigationDetailResponse,
    responses={
        200: {"description": "Successfully retrieved investigation details."},
        404: {"description": "Investigation ID not found."},
        500: {"description": "Internal server error."},
    },
)
def get_investigation_by_id(
    id: str,
    service: InvestigationHistoryService = Depends(get_history_service),
) -> InvestigationDetailResponse:
    """
    Retrieve full details for a single investigation by ID, including its report and multi-agent timeline.
    """
    try:
        detail = service.get_investigation_detail(id)
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation with ID '{id}' not found.",
            )
        return detail
    except HTTPException:
        raise
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.delete(
    "/investigations/{id}",
    response_model=DeleteInvestigationResponse,
    responses={
        200: {"description": "Investigation successfully deleted."},
        404: {"description": "Investigation ID not found."},
        500: {"description": "Internal server error during deletion."},
    },
)
def delete_investigation(
    id: str,
    service: InvestigationHistoryService = Depends(get_history_service),
) -> DeleteInvestigationResponse:
    """
    Delete an investigation record by ID, cascading removal to associated evidence and reports.
    """
    try:
        res = service.delete_investigation(id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation with ID '{id}' not found.",
            )
        return res
    except HTTPException:
        raise
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
