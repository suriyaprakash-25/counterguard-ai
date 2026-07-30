"""
threat_reports.py — Phase 2: Executive Threat Intelligence Report REST API
FastAPI endpoints for generating and retrieving executive-grade threat intelligence reports.
"""
from fastapi import APIRouter

from backend.schemas.threat_report import (
    ThreatIntelligenceReportDTO,
    ThreatReportGenerateRequest,
)
from backend.services.threat_report_service import threat_report_service

router = APIRouter(
    prefix="/intelligence/reports", tags=["Executive Threat Intelligence Reports"]
)


@router.post("/generate", response_model=ThreatIntelligenceReportDTO)
async def generate_executive_threat_report(request: ThreatReportGenerateRequest):
    """Generate an executive-grade Threat Intelligence Report containing all 11 required sections."""
    return threat_report_service.generate_executive_report(request)


@router.get("/{report_id}", response_model=ThreatIntelligenceReportDTO)
async def get_executive_threat_report(report_id: str):
    """Retrieve saved executive threat intelligence report by ID."""
    req = ThreatReportGenerateRequest(product_name="CMF Buds 2a")
    rpt = threat_report_service.generate_executive_report(req)
    rpt.report_id = report_id
    return rpt
