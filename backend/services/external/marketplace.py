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
from backend.services.external.interfaces import MarketplaceAPIWrapperInterface

logger = logging.getLogger(__name__)


class MarketplaceAPIWrapper(MarketplaceAPIWrapperInterface):
    """
    Concrete service wrapper for interacting with Marketplace APIs (Amazon, eBay, Walmart, etc.).
    Supports constructor dependency injection for configuration and optional HTTP client.
    """

    def __init__(
        self,
        config: Optional[ExternalServicesConfig] = None,
        http_client: Optional[Any] = None,
    ):
        self.config = config or external_services_config
        self.http_client = http_client

    def get_listing_details(
        self, listing_id: str, marketplace: str = "amazon"
    ) -> Dict[str, Any]:
        if not listing_id or not str(listing_id).strip():
            raise ExternalServiceInvalidInputError("listing_id must not be empty.")

        marketplace_clean = marketplace.lower().strip()
        logger.info(
            f"Fetching listing details for ID '{listing_id}' on market '{marketplace_clean}'."
        )

        if self.http_client is not None:
            url = f"{self.config.MARKETPLACE_API_BASE_URL}/{marketplace_clean}/listings/{listing_id}"
            try:
                response = self.http_client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.config.MARKETPLACE_API_KEY}"
                    },
                    timeout=self.config.MARKETPLACE_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout fetching listing {listing_id} from {marketplace_clean} API."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error communicating with Marketplace API for listing {listing_id}: {e}"
                ) from e

        # Mock response simulation
        is_suspicious = (
            "suspicious" in str(listing_id).lower() or "fake" in str(listing_id).lower()
        )
        return {
            "listing_id": listing_id,
            "marketplace": marketplace_clean,
            "status": "active",
            "title": f"Official Authentic Product - {listing_id}",
            "current_price": 39.99 if is_suspicious else 199.99,
            "currency": "USD",
            "seller_id": f"SELLER_{listing_id[:4].upper()}",
            "flags": (
                ["potential_counterfeit", "price_anomaly"] if is_suspicious else []
            ),
            "source": "mock_marketplace_wrapper",
        }

    def get_seller_reputation(
        self, seller_id: str, marketplace: str = "amazon"
    ) -> Dict[str, Any]:
        if not seller_id or not str(seller_id).strip():
            raise ExternalServiceInvalidInputError("seller_id must not be empty.")

        marketplace_clean = marketplace.lower().strip()
        logger.info(
            f"Fetching seller reputation for '{seller_id}' on market '{marketplace_clean}'."
        )

        if self.http_client is not None:
            url = f"{self.config.MARKETPLACE_API_BASE_URL}/{marketplace_clean}/sellers/{seller_id}"
            try:
                response = self.http_client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.config.MARKETPLACE_API_KEY}"
                    },
                    timeout=self.config.MARKETPLACE_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout fetching seller {seller_id} reputation."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error fetching seller reputation for {seller_id}: {e}"
                ) from e

        # Mock response simulation
        untrustworthy = (
            "unverified" in str(seller_id).lower() or "fake" in str(seller_id).lower()
        )
        return {
            "seller_id": seller_id,
            "marketplace": marketplace_clean,
            "trust_score": 32.5 if untrustworthy else 94.2,
            "total_reviews": 12 if untrustworthy else 1420,
            "verified_merchant": not untrustworthy,
            "account_age_days": 14 if untrustworthy else 1800,
            "source": "mock_marketplace_wrapper",
        }

    def verify_pricing(
        self, listing_id: str, current_price: float, marketplace: str = "amazon"
    ) -> Dict[str, Any]:
        if not listing_id or not str(listing_id).strip():
            raise ExternalServiceInvalidInputError("listing_id must not be empty.")
        if current_price < 0:
            raise ExternalServiceInvalidInputError("current_price cannot be negative.")

        marketplace_clean = marketplace.lower().strip()
        logger.info(
            f"Verifying pricing for listing '{listing_id}' ({current_price} USD) on '{marketplace_clean}'."
        )

        if self.http_client is not None:
            url = f"{self.config.MARKETPLACE_API_BASE_URL}/{marketplace_clean}/pricing/{listing_id}"
            try:
                response = self.http_client.get(
                    url,
                    params={"current_price": current_price},
                    headers={
                        "Authorization": f"Bearer {self.config.MARKETPLACE_API_KEY}"
                    },
                    timeout=self.config.MARKETPLACE_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout checking price for listing {listing_id}."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error checking pricing for listing {listing_id}: {e}"
                ) from e

        # Mock response simulation
        average_msrp = 200.0
        discount_percentage = max(
            0.0, round(100 * (1.0 - current_price / average_msrp), 2)
        )
        is_anomaly = discount_percentage > 60.0

        return {
            "listing_id": listing_id,
            "current_price": current_price,
            "average_historical_msrp": average_msrp,
            "discount_percentage": discount_percentage,
            "price_anomaly_detected": is_anomaly,
            "risk_level": "HIGH" if is_anomaly else "LOW",
            "source": "mock_marketplace_wrapper",
        }
