import os
import requests
from typing import Dict, Any, Optional

# Read API URL from environment variables, fallback to localhost for development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def health() -> bool:
    """
    Check if the backend API is online.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def investigate(listing_url: str, marketplace: str) -> Optional[Dict[str, Any]]:
    """
    Call the investigate endpoint.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/investigate",
            json={
                "listing_url": listing_url,
                "marketplace": marketplace
            },
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error calling investigate API: {e}")
        return None
