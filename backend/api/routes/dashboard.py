from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.database.repositories.dashboard_repo import DashboardRepository
from backend.dependencies import neo4j_client
from backend.models.alert import AlertModel
from backend.models.investigation import InvestigationModel
from backend.models.report import ReportModel
from backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard")


def get_dashboard_service(
    session: Session = Depends(get_db_session),
) -> DashboardService:
    repo = DashboardRepository(session, neo4j_client)
    return DashboardService(repo)


@router.get("/metrics")
def get_metrics(service: DashboardService = Depends(get_dashboard_service)):
    return {"data": service.get_summary_metrics()}


@router.get("/marketplaces")
def get_marketplaces(service: DashboardService = Depends(get_dashboard_service)):
    return {"data": service.get_marketplace_metrics()}


@router.get("/risk-trend")
def get_risk_trend(service: DashboardService = Depends(get_dashboard_service)):
    return {"data": service.get_risk_trend()}


@router.get("/system-health")
def get_system_health(service: DashboardService = Depends(get_dashboard_service)):
    return {"data": service.get_system_health()}


@router.get("/fraud-nodes")
def get_fraud_nodes(service: DashboardService = Depends(get_dashboard_service)):
    return {"data": service.get_fraud_node_preview()}


@router.get("/summary")
def get_summary(service: DashboardService = Depends(get_dashboard_service)):
    """Alias for /metrics — some frontend widgets call /summary."""
    return {"data": service.get_summary_metrics()}


@router.get("/activity")
def get_recent_activity(session: Session = Depends(get_db_session)):
    """Return the 10 most recently updated investigations as activity feed."""
    investigations = (
        session.query(InvestigationModel)
        .order_by(InvestigationModel.updated_at.desc())
        .limit(10)
        .all()
    )
    items = []
    for inv in investigations:
        items.append(
            {
                "id": inv.id,
                "type": "investigation",
                "status": inv.status,
                "marketplace": inv.marketplace,
                "listing_url": inv.listing_url,
                "timestamp": inv.updated_at.isoformat()
                if isinstance(inv.updated_at, datetime)
                else str(inv.updated_at),
            }
        )
    return {"data": items}


@router.get("/investigation-trend")
def get_investigation_trend(session: Session = Depends(get_db_session)):
    """Return investigations created per day for the last 7 days."""
    trend = []
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        count = (
            session.query(func.count(InvestigationModel.id))
            .filter(
                InvestigationModel.created_at >= day_start,
                InvestigationModel.created_at < day_end,
            )
            .scalar()
        ) or 0
        trend.append({"date": day.isoformat(), "count": count})
    return {"data": trend}


@router.get("/risk-distribution")
def get_risk_distribution(session: Session = Depends(get_db_session)):
    """Return count of investigations grouped by risk_level."""
    results = (
        session.query(ReportModel.risk_level, func.count(ReportModel.id).label("count"))
        .group_by(ReportModel.risk_level)
        .all()
    )
    distribution = [{"level": row.risk_level, "count": row.count} for row in results]
    if not distribution:
        distribution = [
            {"level": "HIGH", "count": 0},
            {"level": "MEDIUM", "count": 0},
            {"level": "LOW", "count": 0},
        ]
    return {"data": distribution}


@router.get("/active-alerts")
def get_active_alerts(session: Session = Depends(get_db_session)):
    """Return the most recent alerts (state=new)."""
    alerts = (
        session.query(AlertModel)
        .filter(AlertModel.state == "new")
        .order_by(AlertModel.time.desc())
        .limit(5)
        .all()
    )
    items = []
    for alert in alerts:
        items.append(
            {
                "id": alert.id,
                "level": alert.level,
                "headline": alert.headline,
                "platform": alert.platform,
                "time": alert.time.isoformat() + "Z"
                if isinstance(alert.time, datetime)
                else str(alert.time),
                "state": alert.state,
                "risk": alert.risk,
            }
        )
    return {"data": items}


@router.get("/suspicious-sellers")
def get_suspicious_sellers(service: DashboardService = Depends(get_dashboard_service)):
    """Return top suspicious merchant leaderboard."""
    return {"data": service.get_suspicious_sellers()}


@router.get("/agent-states")
def get_agent_states(service: DashboardService = Depends(get_dashboard_service)):
    """Return LangGraph swarm agent execution states."""
    return {"data": service.get_swarm_agent_states()}
