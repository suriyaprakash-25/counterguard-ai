from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.alert import AlertModel


class AlertsRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_alerts(self, limit: int = 20) -> List[AlertModel]:
        return self._session.query(AlertModel).order_by(AlertModel.time.desc()).limit(limit).all()

    def get_alert_by_id(self, alert_id: str) -> Optional[AlertModel]:
        return self._session.query(AlertModel).filter(AlertModel.id == alert_id).first()

    def acknowledge_alert(self, alert_id: str) -> bool:
        alert = self.get_alert_by_id(alert_id)
        if alert:
            alert.state = "acknowledged"
            self._session.commit()
            return True
        return False
