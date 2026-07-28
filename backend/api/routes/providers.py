import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

from backend.schemas.product_intelligence import ProviderHealth
from backend.services.provider_health_service import ProviderHealthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/health", response_model=Dict[str, List[ProviderHealth]])
def get_provider_health():
    """
    GET /api/v1/providers/health
    Returns real-time health metrics, average response latency, success rate,
    total queries, and status for all product search providers.
    """
    try:
        health_service = ProviderHealthService()
        metrics = health_service.get_health_metrics()
        return {"providers": metrics}
    except Exception as e:
        logger.error(f"Error fetching provider health metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch provider health: {e}")
