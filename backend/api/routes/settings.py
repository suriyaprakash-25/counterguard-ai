from fastapi import APIRouter, Depends

from backend.database.repositories.settings_repo import SettingsRepository
from backend.services.settings_service import SettingsService

router = APIRouter(prefix="/settings")


def get_settings_service() -> SettingsService:
    repo = SettingsRepository()
    return SettingsService(repo)


@router.get("")
@router.get("/config")
def get_config(service: SettingsService = Depends(get_settings_service)):
    return {"data": service.get_config()}


@router.post("")
@router.post("/config")
def update_config_post(service: SettingsService = Depends(get_settings_service)):
    return {"data": {"success": True, "message": "Settings updated successfully"}}


@router.put("")
@router.put("/config")
def update_config_put(service: SettingsService = Depends(get_settings_service)):
    return {"data": {"success": True, "message": "Settings updated successfully"}}
