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
    service: AlertsService = Depends(get_alerts_service),
):
    return {"data": service.get_alerts(limit)}


@router.get("/feed")
def get_deduplicated_alert_feed(severity: str = Query(default=None)):
    """Fetch deduplicated real-time alert feed from AlertService."""
    from backend.services.alert_service import alert_service

    return alert_service.get_alert_feed(severity)


@router.post("/test-webhook")
def test_webhook_delivery(req: dict):
    """Trigger test webhook POST delivery."""
    from backend.schemas.watchlist import WebhookTestRequest
    from backend.services.alert_service import alert_service

    target_url = req.get("target_url", "https://api.counterguard.ai/v1/webhooks/alerts")
    return alert_service.test_webhook_delivery(
        WebhookTestRequest(target_url=target_url)
    )


@router.get("/{id}")
def get_alert_details(id: str, service: AlertsService = Depends(get_alerts_service)):
    alert = service.get_alert_by_id(id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"data": alert}


@router.post("/{id}/acknowledge")
def acknowledge_alert(id: str, service: AlertsService = Depends(get_alerts_service)):
    success = service.acknowledge_alert(id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"data": {"success": True}}


@router.get("/feed")
def get_deduplicated_alert_feed(severity: str = Query(default=None)):
    """Fetch deduplicated real-time alert feed from AlertService."""
    from backend.services.alert_service import alert_service

    return alert_service.get_alert_feed(severity)


@router.post("/test-webhook")
def test_webhook_delivery(req: dict):
    """Trigger test webhook POST delivery."""
    from backend.schemas.watchlist import WebhookTestRequest
    from backend.services.alert_service import alert_service

    target_url = req.get("target_url", "https://api.counterguard.ai/v1/webhooks/alerts")
    return alert_service.test_webhook_delivery(
        WebhookTestRequest(target_url=target_url)
    )
