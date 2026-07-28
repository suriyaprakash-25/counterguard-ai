from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.database.repositories.alerts_repo import AlertsRepository
from backend.services.alerts_service import AlertsService

router = APIRouter(prefix="/alerts")


def get_alerts_service(
    session: Session = Depends(get_db_session),
) -> AlertsService:
    repo = AlertsRepository(session)
    return AlertsService(repo)


@router.get("")
def list_alerts(
    limit: int = Query(20, ge=1, le=100),
    service: AlertsService = Depends(get_alerts_service)
):
    return {"data": service.get_alerts(limit)}


@router.get("/{id}")
def get_alert_details(
    id: str,
    service: AlertsService = Depends(get_alerts_service)
):
    alert = service.get_alert_by_id(id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"data": alert}


@router.post("/{id}/acknowledge")
def acknowledge_alert(
    id: str,
    service: AlertsService = Depends(get_alerts_service)
):
    success = service.acknowledge_alert(id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"data": {"success": True}}
