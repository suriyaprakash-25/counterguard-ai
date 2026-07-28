from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.database.repositories.analytics_repo import AnalyticsRepository
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics")


def get_analytics_service(session: Session = Depends(get_db_session)) -> AnalyticsService:
    repo = AnalyticsRepository(session)
    return AnalyticsService(repo)


@router.get("")
def get_dashboard(service: AnalyticsService = Depends(get_analytics_service)):
    return {"data": service.get_dashboard_data()}
