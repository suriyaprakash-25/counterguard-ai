"""
closed_loop.py — Phase 2: Closed-Loop Intelligence REST API Routes
FastAPI endpoints for triggering autonomous closed-loop feedback cycles and reading pipeline execution telemetry.
"""
from fastapi import APIRouter, HTTPException, Query

from backend.schemas.closed_loop import ClosedLoopTelemetryDTO, ClosedLoopTriggerRequest
from backend.services.closed_loop_intelligence_engine import (
    closed_loop_intelligence_engine,
)

router = APIRouter(
    prefix="/intelligence/closed-loop", tags=["Closed-Loop Intelligence Engine"]
)


@router.post("/trigger", response_model=ClosedLoopTelemetryDTO)
async def trigger_closed_loop_cycle(request: ClosedLoopTriggerRequest):
    """Trigger an 8-stage autonomous closed-loop feedback pipeline for a completed investigation."""
    try:
        return closed_loop_intelligence_engine.trigger_closed_loop_pipeline(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/telemetry", response_model=ClosedLoopTelemetryDTO)
async def get_closed_loop_telemetry(case_id: str = Query(default="INV-8901")):
    """Fetch 8-stage pipeline telemetry logs and evolution metrics for a case."""
    req = ClosedLoopTriggerRequest(case_id=case_id, product_name="CMF Buds 2a")
    return closed_loop_intelligence_engine.trigger_closed_loop_pipeline(req)
