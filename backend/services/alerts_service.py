from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.database.repositories.alerts_repo import AlertsRepository


class AlertsService:
    def __init__(self, repo: AlertsRepository):
        self._repo = repo

    def _format_time(self, val: Any) -> str:
        if isinstance(val, datetime):
            return val.isoformat() + "Z"
        return str(val) if val else datetime.utcnow().isoformat() + "Z"

    def get_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        alerts = self._repo.get_alerts(limit)
        return [
            {
                "_id": alert.id,
                "level": alert.level,
                "headline": alert.headline,
                "platform": alert.platform,
                "time": self._format_time(alert.time),
                "case_id": alert.case_id,
                "state": alert.state,
                "risk": alert.risk,
                "category": alert.category,
                "desc": alert.desc,
                "entities": alert.entities or [],
                "actions": alert.actions or []
            }
            for alert in alerts
        ]

    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        alert = self._repo.get_alert_by_id(alert_id)
        if not alert:
            return None
        return {
            "_id": alert.id,
            "level": alert.level,
            "headline": alert.headline,
            "platform": alert.platform,
            "time": self._format_time(alert.time),
            "case_id": alert.case_id,
            "state": alert.state,
            "risk": alert.risk,
            "category": alert.category,
            "desc": alert.desc,
            "entities": alert.entities or [],
            "actions": alert.actions or []
        }

    def acknowledge_alert(self, alert_id: str) -> bool:
        return self._repo.acknowledge_alert(alert_id)
