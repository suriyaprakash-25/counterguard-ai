from typing import Dict, Any, List
from backend.database.repositories.intelligence_repo import IntelligenceRepository


class IntelligenceService:
    def __init__(self, repo: IntelligenceRepository):
        self._repo = repo

    def get_summary(self) -> Dict[str, Any]:
        return self._repo.get_summary()

    def get_sellers(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._repo.get_sellers(limit)

    def get_fraud_rings(self) -> List[Dict[str, Any]]:
        return self._repo.get_fraud_rings()

    def get_known_patterns(self) -> List[Dict[str, Any]]:
        return self._repo.get_known_patterns()

    def get_repeated_images(self) -> List[Dict[str, Any]]:
        return self._repo.get_repeated_images()

    def get_repeated_phones(self) -> List[Dict[str, Any]]:
        return self._repo.get_repeated_phones()

    def get_repeated_invoices(self) -> List[Dict[str, Any]]:
        return self._repo.get_repeated_invoices()

    def get_memory_insights(self) -> List[Dict[str, Any]]:
        return self._repo.get_memory_insights()
