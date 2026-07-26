import logging
from typing import Any, Dict, Optional

from backend.config.external_services import (
    ExternalServicesConfig,
    external_services_config,
)
from backend.services.external.exceptions import (
    ExternalServiceError,
    ExternalServiceInvalidInputError,
    ExternalServiceTimeoutError,
)
from backend.services.external.interfaces import GoogleSearchWrapperInterface

logger = logging.getLogger(__name__)


class GoogleSearchWrapper(GoogleSearchWrapperInterface):
    """
    Concrete service wrapper for Google Custom Search & Reverse Image OSINT.
    Supports constructor dependency injection for config and optional HTTP client.
    """

    def __init__(
        self,
        config: Optional[ExternalServicesConfig] = None,
        http_client: Optional[Any] = None,
    ):
        self.config = config or external_services_config
        self.http_client = http_client

    def search_web(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        if not query or not str(query).strip():
            raise ExternalServiceInvalidInputError("Search query must not be empty.")
        if num_results <= 0:
            raise ExternalServiceInvalidInputError("num_results must be positive.")

        query_clean = query.strip()
        logger.info(
            f"Executing Google OSINT web search for query: '{query_clean}' (num={num_results})."
        )

        if self.http_client is not None:
            params = {
                "key": self.config.GOOGLE_SEARCH_API_KEY,
                "cx": self.config.GOOGLE_SEARCH_ENGINE_ID,
                "q": query_clean,
                "num": num_results,
            }
            try:
                response = self.http_client.get(
                    self.config.GOOGLE_SEARCH_API_URL,
                    params=params,
                    timeout=self.config.GOOGLE_SEARCH_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout executing Google search for '{query_clean}'."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error executing Google web search for '{query_clean}': {e}"
                ) from e

        # Mock response simulation
        results = []
        for idx in range(1, num_results + 1):
            results.append(
                {
                    "title": f"Intelligence Match #{idx}: '{query_clean}'",
                    "url": f"https://intel-source.example.org/doc/{idx}?q={query_clean}",
                    "snippet": f"Verified open-source finding indicating potential distribution channels and community reports for {query_clean}.",
                    "rank": idx,
                }
            )

        return {
            "query": query_clean,
            "total_estimated_matches": 8420,
            "results": results,
            "source": "mock_google_search_wrapper",
        }

    def search_images(
        self, image_url: str, similarity_threshold: float = 0.80
    ) -> Dict[str, Any]:
        if not image_url or not str(image_url).strip():
            raise ExternalServiceInvalidInputError("image_url must not be empty.")
        if not (0.0 <= similarity_threshold <= 1.0):
            raise ExternalServiceInvalidInputError(
                "similarity_threshold must be between 0.0 and 1.0."
            )

        image_url_clean = image_url.strip()
        logger.info(
            f"Executing reverse image search for: '{image_url_clean}' (threshold={similarity_threshold})."
        )

        if self.http_client is not None:
            params = {
                "key": self.config.GOOGLE_SEARCH_API_KEY,
                "searchType": "image",
                "imgUrl": image_url_clean,
            }
            try:
                response = self.http_client.get(
                    self.config.GOOGLE_SEARCH_API_URL,
                    params=params,
                    timeout=self.config.GOOGLE_SEARCH_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    "Timeout executing reverse image search."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error executing reverse image search for '{image_url_clean}': {e}"
                ) from e

        # Mock response simulation
        is_suspicious = (
            "fake" in image_url_clean.lower() or "replica" in image_url_clean.lower()
        )
        matches = [
            {
                "matched_url": "https://official-brand-catalog.example.com/item_original.png",
                "domain": "official-brand-catalog.example.com",
                "similarity_score": 0.98,
                "is_authorized_domain": True,
                "description": "Original manufacturer studio photography.",
            },
            {
                "matched_url": "https://unauthorized-grey-market.example.net/copy_photo.jpg",
                "domain": "unauthorized-grey-market.example.net",
                "similarity_score": 0.92 if is_suspicious else 0.45,
                "is_authorized_domain": False,
                "description": "Unverified replica store using duplicate catalog media.",
            },
        ]

        filtered_matches = [
            m for m in matches if m["similarity_score"] >= similarity_threshold
        ]
        stolen_image = any(not m["is_authorized_domain"] for m in filtered_matches)

        return {
            "queried_image_url": image_url_clean,
            "matches_found": len(filtered_matches),
            "similarity_threshold": similarity_threshold,
            "stolen_image": stolen_image,
            "matches": filtered_matches,
            "source": "mock_google_search_wrapper",
        }
