from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.database.repositories.intelligence_repo import IntelligenceRepository
from backend.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/intelligence")


def get_intelligence_service(session: Session = Depends(get_db_session)) -> IntelligenceService:
    repo = IntelligenceRepository(session)
    return IntelligenceService(repo)


@router.get("/summary")
def get_summary(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_summary()}


@router.get("/sellers")
def get_sellers(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_sellers()}


@router.get("/rings")
def get_fraud_rings(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_fraud_rings()}


@router.get("/patterns")
def get_patterns(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_known_patterns()}


@router.get("/images")
def get_images(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_repeated_images()}


@router.get("/phones")
def get_phones(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_repeated_phones()}


@router.get("/invoices")
def get_invoices(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_repeated_invoices()}


@router.get("/memory")
def get_memory_insights(service: IntelligenceService = Depends(get_intelligence_service)):
    return {"data": service.get_memory_insights()}
