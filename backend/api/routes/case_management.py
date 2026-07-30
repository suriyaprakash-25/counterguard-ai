"""
case_management.py — Phase 2: Collaborative Investigation Case REST API Routes
FastAPI endpoints for managing 7 case states, analyst assignments, comments, and auditable action timelines.
"""
from typing import List

from fastapi import APIRouter, HTTPException, Query

from backend.schemas.case_management import (
    CaseAssignRequest,
    CaseCommentDTO,
    CaseCommentRequest,
    CaseStateUpdateRequest,
    CollaborativeCaseDTO,
)
from backend.services.case_management_service import case_management_service

router = APIRouter(prefix="/cases", tags=["Collaborative Case Management"])


@router.get("", response_model=List[CollaborativeCaseDTO])
async def list_collaborative_cases(filter_type: str = Query(default="all")):
    """List cases with filters: all, my_cases, team, high_priority, overdue."""
    return case_management_service.get_cases(filter_type)


@router.get("/{case_id}", response_model=CollaborativeCaseDTO)
async def get_collaborative_case_details(case_id: str):
    """Fetch detailed case info with full audit timeline."""
    c = case_management_service.get_case_by_id(case_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
    return c


@router.put("/{case_id}/status", response_model=CollaborativeCaseDTO)
async def update_case_lifecycle_state(case_id: str, request: CaseStateUpdateRequest):
    """Transition case state through the 7 lifecycle states: Open, Assigned, Investigating, Evidence Collected, Legal Review, Resolved, Closed."""
    try:
        return case_management_service.update_case_state(case_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/comments", response_model=CaseCommentDTO)
async def add_analyst_comment(case_id: str, request: CaseCommentRequest):
    """Post an analyst comment or investigation note to a case."""
    try:
        return case_management_service.add_comment(case_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{case_id}/assign", response_model=CollaborativeCaseDTO)
async def assign_case_to_analyst(case_id: str, request: CaseAssignRequest):
    """Reassign case to an analyst."""
    try:
        return case_management_service.assign_case(case_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
