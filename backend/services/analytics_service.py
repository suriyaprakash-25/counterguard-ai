from typing import Dict, Any
from backend.database.repositories.analytics_repo import AnalyticsRepository

class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self._repo = repo

    def get_dashboard_data(self) -> Dict[str, Any]:
        return self._repo.get_dashboard_data()
