"""
Centralized HTTP client for interacting with the CounterGuard FastAPI backend.
Provides fault-tolerant helpers and automatic Pydantic model serialization.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

from frontend.streamlit_app.models.investigation import InvestigationState

logger = logging.getLogger(__name__)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEFAULT_TIMEOUT_SECONDS = 15


def _get(path: str, timeout: int = 5) -> Optional[requests.Response]:
    """
    Execute a resilient GET request against the backend endpoint.

    Args:
        path: Relative URL endpoint path starting with slash.
        timeout: Maximum execution duration in seconds before abort.
    """
    try:
        response = requests.get(f"{API_BASE_URL}{path}", timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        logger.error("GET request failed for path '%s': %s", path, exc)
        return None


def _post(
    path: str,
    payload: Dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Optional[requests.Response]:
    """
    Execute a resilient JSON POST request against the backend endpoint.

    Args:
        path: Relative URL endpoint path starting with slash.
        payload: Dictionary to serialize into JSON body.
        timeout: Maximum execution duration in seconds before abort.
    """
    try:
        response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        logger.error("POST request failed for path '%s': %s", path, exc)
        return None


def health() -> bool:
    """
    Verify if the remote CounterGuard API instance is actively operational.

    Returns:
        True if endpoint responds with 200 OK status, False otherwise.
    """
    response = _get("/health", timeout=5)
    return response is not None and response.status_code == 200


def investigate(listing_url: str, marketplace: str) -> Optional[InvestigationState]:
    """
    Request automated agent investigation for a target commodity listing.

    Args:
        listing_url: Direct link to the suspicious item on retailer site.
        marketplace: Designated hosting trading portal name.

    Returns:
        Validated Pydantic representation of the resulting investigation.
    """
    payload = {"listing_url": listing_url, "marketplace": marketplace}
    response = _post("/api/v1/investigate", payload=payload)
    if response is None:
        return None
    return InvestigationState.model_validate(response.json())
