from typing import Dict, Any
from backend.database.repositories.settings_repo import SettingsRepository

class SettingsService:
    def __init__(self, repo: SettingsRepository):
        self._repo = repo

    def get_config(self) -> Dict[str, Any]:
        return self._repo.get_config()
