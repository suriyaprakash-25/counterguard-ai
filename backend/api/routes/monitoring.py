"""
monitoring.py — Phase 8: Proactive Continuous Monitoring REST API Routes
FastAPI endpoints for monitoring jobs, execution history, manual triggers, and pause/resume controls.
"""
from typing import List

from fastapi import APIRouter, HTTPException, Query

from backend.schemas.monitoring import (
    MonitoringHistoryRecordDTO,
    MonitoringJobDTO,
    MonitoringStatusResponse,
)
from backend.services.monitoring_orchestrator import monitoring_orchestrator
from backend.services.monitoring_scheduler import monitoring_scheduler

router = APIRouter(prefix="/monitor", tags=["Proactive Continuous Monitoring"])


@router.get("/jobs", response_model=MonitoringStatusResponse)
@router.get("/status", response_model=MonitoringStatusResponse)
async def get_monitoring_jobs_status():
    """Fetch status dashboard metrics and active/paused continuous monitoring jobs."""
    return monitoring_orchestrator.get_monitoring_status()


@router.get("/history", response_model=List[MonitoringHistoryRecordDTO])
async def get_monitoring_execution_history():
    """Fetch log history of continuous monitoring pipeline executions."""
    return monitoring_orchestrator.get_execution_history()


@router.post("/run")
async def trigger_monitoring_job(job_id: str = Query(default="job-cmf-buds")):
    """Trigger immediate execution of continuous discovery scan & auto-investigation for a job."""
    try:
        return await monitoring_orchestrator.run_monitoring_cycle(job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pause", response_model=MonitoringJobDTO)
async def pause_monitoring_job(job_id: str = Query(...)):
    """Pause a continuous monitoring job schedule."""
    try:
        return monitoring_scheduler.pause_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resume", response_model=MonitoringJobDTO)
async def resume_monitoring_job(job_id: str = Query(...)):
    """Resume a paused continuous monitoring job schedule."""
    try:
        return monitoring_scheduler.resume_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
