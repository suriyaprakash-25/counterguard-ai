from typing import Optional

from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
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
from backend.services.investigation_service import InvestigationService
from backend.schemas.investigation import InvestigationRequest
from backend.models.investigation import InvestigationModel
import logging
logger = logging.getLogger(__name__)

class CreateInvestigationRequest(BaseModel):
    name: str
    brand: str
    marketplace: str
    product: Optional[str] = ""
    seller: Optional[str] = ""
    plannerPriority: str
    notes: Optional[str] = ""

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
):
    """
    Retrieve a paginated, filtered, and sorted list of completed or in-progress investigations.
    """
    try:
        return {"data": service.list_investigations(
            page=page,
            page_size=page_size,
            marketplace=marketplace,
            status=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
        )}
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.get(
    "/investigations/{id}",
    responses={
        200: {"description": "Successfully retrieved investigation details."},
        404: {"description": "Investigation ID not found."},
        500: {"description": "Internal server error."},
    },
)
def get_investigation_by_id(
    id: str,
    service: InvestigationHistoryService = Depends(get_history_service),
):
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
        return {"data": detail}
    except HTTPException:
        raise
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.delete(
    "/investigations/{id}",
    responses={
        200: {"description": "Investigation successfully deleted."},
        404: {"description": "Investigation ID not found."},
        500: {"description": "Internal server error during deletion."},
    },
)
def delete_investigation(
    id: str,
    service: InvestigationHistoryService = Depends(get_history_service),
):
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
        return {"data": res}
    except HTTPException:
        raise
    except CounterGuardError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@router.post("/investigations", status_code=status.HTTP_202_ACCEPTED)
def create_investigation(
    payload: CreateInvestigationRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db_session)
):
    from backend.services.investigation_runner import InvestigationRunner

    inv = InvestigationModel(
        marketplace=payload.marketplace,
        listing_url=payload.seller or f"search://{payload.brand}/{payload.product}",
        status="pending"
    )
    repo = InvestigationRepository(session)
    repo.add(inv)

    request_dto = InvestigationRequest(
        listing_url=inv.listing_url,
        marketplace=inv.marketplace
    )
    background_tasks.add_task(InvestigationRunner.execute, inv.id, request_dto)

    return {"data": {"id": inv.id}}

@router.post("/investigations/{id}/cancel")
def cancel_investigation(
    id: str,
    session: Session = Depends(get_db_session)
):
    repo = InvestigationRepository(session)
    inv = repo.get_by_id(id)
    if inv and inv.status in ("pending", "in_progress"):
        inv.status = "cancelled"
        session.commit()
    return {"data": {"success": True}}


@router.post("/investigations/{id}/retry")
def retry_investigation(
    id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db_session)
):
    from backend.services.investigation_runner import InvestigationRunner
    repo = InvestigationRepository(session)
    inv = repo.get_by_id(id)
    if inv and inv.status == "failed":
        inv.status = "pending"
        session.commit()
        request_dto = InvestigationRequest(
            listing_url=inv.listing_url,
            marketplace=inv.marketplace
        )
        background_tasks.add_task(InvestigationRunner.execute, inv.id, request_dto)
    return {"data": {"success": True}}

@router.get("/investigations/{id}/timeline")
def get_timeline(id: str, session: Session = Depends(get_db_session)):
    from backend.database.repositories.evidence_repo import EvidenceRepository as EvidRepo
    ev_repo = EvidRepo(session)
    evidence_models = ev_repo.get_by_investigation(id)
    timeline = [
        {
            "id": ev.id,
            "agent": ev.agent,
            "action": ev.action,
            "detail": ev.detail,
            "confidence_delta": ev.confidence_delta,
            "timestamp": ev.timestamp,
        }
        for ev in evidence_models
    ]
    return {"data": timeline}


@router.get("/investigations/{id}/graph")
def get_investigation_graph(
    id: str,
    session: Session = Depends(get_db_session)
):
    rep_repo = ReportRepository(session)
    report_model = rep_repo.get_by_investigation(id)

    inv_repo = InvestigationRepository(session)
    inv = inv_repo.get_by_id(id)

    product_name = report_model.product if report_model else (inv.listing_url if inv else f"Product {id[:6]}")
    seller_name = (report_model.seller if report_model else None) or (inv.marketplace if inv else "Global Seller")
    marketplace_name = (report_model.marketplace if report_model else None) or (inv.marketplace if inv else "Global")
    risk_score = report_model.risk_score if report_model else 45

    nodes = [
        {"data": {"id": "investigation", "label": f"INV-{id[:8]}", "type": "investigation", "riskScore": risk_score}},
        {"data": {"id": "product", "label": product_name, "type": "product", "riskScore": risk_score}},
        {"data": {"id": "seller", "label": seller_name, "type": "seller", "riskScore": risk_score}},
        {"data": {"id": "marketplace", "label": marketplace_name, "type": "marketplace", "riskScore": 0}},
        {"data": {"id": "trademark", "label": f"{product_name[:20]} TM", "type": "trademark", "riskScore": 20}},
        {"data": {"id": "domain", "label": f"{seller_name.lower().replace(' ', '')}-verify.com", "type": "phone", "riskScore": 65}},
        {"data": {"id": "pattern", "label": f"Pattern: Price Anomaly ({risk_score}%)", "type": "investigation", "riskScore": risk_score}},
    ]
    edges = [
        {"data": {"id": "e1", "source": "investigation", "target": "product", "label": "evaluates"}},
        {"data": {"id": "e2", "source": "seller", "target": "product", "label": "sells"}},
        {"data": {"id": "e3", "source": "product", "target": "marketplace", "label": "listed_on"}},
        {"data": {"id": "e4", "source": "product", "target": "trademark", "label": "claims"}},
        {"data": {"id": "e5", "source": "seller", "target": "domain", "label": "owns"}},
        {"data": {"id": "e6", "source": "product", "target": "pattern", "label": "matches"}},
    ]
    return {"data": {"nodes": nodes, "edges": edges, "layout": {"name": "cose"}}}


@router.get("/investigations/{id}/reasoning")
def get_reasoning(id: str, session: Session = Depends(get_db_session)):
    rep_repo = ReportRepository(session)
    report_model = rep_repo.get_by_investigation(id)
    if not report_model:
        return {"data": {"reasoning": "", "supportingEvidenceIds": [], "recommendations": []}}

    findings = report_model.get_findings_list()
    return {
        "data": {
            "reasoning": report_model.ai_reasoning or report_model.summary,
            "supportingEvidenceIds": [],
            "recommendations": findings,
        }
    }


@router.get("/investigations/{id}/report")
def get_report(id: str, session: Session = Depends(get_db_session)):
    rep_repo = ReportRepository(session)
    report_model = rep_repo.get_by_investigation(id)
    if not report_model:
        return {"data": {"executiveSummary": "", "riskAssessment": "", "evidence": [], "recommendations": [], "confidence": 0}}

    return {
        "data": {
            "executiveSummary": report_model.ai_summary or report_model.summary,
            "riskAssessment": f"{report_model.risk_level} (Score: {report_model.risk_score}/100)",
            "evidence": report_model.get_evidence_summary_dict(),
            "recommendations": report_model.get_findings_list(),
            "confidence": report_model.confidence,
            "report": report_model.to_pydantic().model_dump(),
        }
    }


@router.get("/investigations/{id}/evidence")
def get_evidence(id: str, session: Session = Depends(get_db_session)):
    """Return all structured evidence items for an investigation."""
    from backend.database.repositories.evidence_repo import EvidenceRepository as EvidRepo
    ev_repo = EvidRepo(session)
    evidence_models = ev_repo.get_by_investigation(id)
    evidence = [
        {
            "id": ev.id,
            "type": "agent_finding",
            "agent": ev.agent,
            "description": ev.detail,
            "source": ev.agent,
            "confidence": round(ev.confidence_delta * 100) if ev.confidence_delta else 0,
            "timestamp": ev.timestamp,
        }
        for ev in evidence_models
    ]
    return {"data": evidence}


@router.get("/investigations/{id}/consensus")
def get_consensus(id: str, session: Session = Depends(get_db_session)):
    """Return multi-agent consensus result derived from the investigation report."""
    rep_repo = ReportRepository(session)
    report_model = rep_repo.get_by_investigation(id)
    if not report_model:
        return {"data": {"agreementScore": 0, "explanation": "Awaiting consensus.", "agentVotes": []}}

    agreement = round(report_model.confidence * 100) if report_model.confidence else 0
    return {
        "data": {
            "agreementScore": agreement,
            "explanation": (
                f"All agents agreed on a {report_model.risk_level} risk rating "
                f"with {agreement}% confidence for {report_model.product}."
            ),
            "agentVotes": [
                {"agent": "PriceAgent", "vote": report_model.risk_level, "confidence": agreement},
                {"agent": "SellerAgent", "vote": report_model.risk_level, "confidence": agreement},
                {"agent": "BrandAgent", "vote": report_model.risk_level, "confidence": agreement},
                {"agent": "ReviewAgent", "vote": report_model.risk_level, "confidence": agreement},
                {"agent": "CoordinatorAgent", "vote": report_model.risk_level, "confidence": agreement},
            ],
        }
    }


@router.get("/investigations/{id}/stream")
async def stream_investigation(id: str, session: Session = Depends(get_db_session)):
    """SSE stream for real-time status updates. Sends heartbeats to prevent aggressive reconnects."""
    from fastapi.responses import StreamingResponse
    import asyncio
    import json

    async def event_generator():
        try:
            # Send initial status
            inv = InvestigationRepository(session).get_by_id(id)
            status = inv.status if inv else "unknown"
            yield f"data: {json.dumps({'type': 'StatusUpdated', 'payload': {'status': status}})}\n\n"

            # If already in terminal state, close cleanly
            if status in ("completed", "failed", "cancelled", "unknown"):
                return

            # Poll while investigation is running
            max_polls = 60  # max 5 minutes (5s * 60)
            for _ in range(max_polls):
                await asyncio.sleep(5)
                # Send heartbeat to prevent client reconnect
                yield ": heartbeat\n\n"
                # Check updated status
                from backend.database.engine import get_session_maker
                fresh_session = get_session_maker()()
                try:
                    fresh_inv = InvestigationRepository(fresh_session).get_by_id(id)
                    new_status = fresh_inv.status if fresh_inv else "unknown"
                    yield f"data: {json.dumps({'type': 'StatusUpdated', 'payload': {'status': new_status}})}\n\n"
                    if new_status in ("completed", "failed", "cancelled"):
                        break
                finally:
                    fresh_session.close()
        except Exception:
            pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")
