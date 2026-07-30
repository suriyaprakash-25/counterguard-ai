from typing import Any, Dict, List

from backend.database.repositories.dashboard_repo import DashboardRepository


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self._repo = repo

    def get_summary_metrics(self) -> Dict[str, Any]:
        return self._repo.get_summary_metrics()

    def get_marketplace_metrics(self) -> List[Dict[str, Any]]:
        return self._repo.get_marketplace_metrics()

    def get_risk_trend(self) -> List[Dict[str, Any]]:
        return self._repo.get_risk_trend()

    def get_system_health(self) -> Dict[str, str]:
        # Return static healthy for now, can be dynamically checked
        return {
            "fastapi": "healthy",
            "langgraph": "healthy",
            "sqlite": "healthy",
            "neo4j": "healthy",
            "chromadb": "healthy",
            "graphrag": "healthy",
            "automation": "healthy",
        }

    def get_fraud_node_preview(self) -> List[Dict[str, Any]]:
        return self._repo.get_fraud_node_preview()

    def get_suspicious_sellers(self) -> List[Dict[str, Any]]:
        return self._repo.get_suspicious_sellers()

    def get_swarm_agent_states(self) -> List[Dict[str, Any]]:
        return self._repo.get_swarm_agent_states()
