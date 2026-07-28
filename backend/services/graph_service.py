from typing import Dict, Any, Optional
from backend.database.repositories.graph_repo import GraphRepository


class GraphService:
    def __init__(self, repo: GraphRepository):
        self._repo = repo

    def get_data(self) -> Dict[str, Any]:
        return self._repo.get_data()

    def get_stats(self) -> Dict[str, Any]:
        return self._repo.get_stats()

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self._repo.get_node(node_id)
