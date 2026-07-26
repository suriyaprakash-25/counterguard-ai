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
from backend.services.external.interfaces import BrandRegistryWrapperInterface

logger = logging.getLogger(__name__)


class BrandRegistryWrapper(BrandRegistryWrapperInterface):
    """
    Concrete service wrapper for global Brand and Trademark registries.
    Supports constructor dependency injection for config and optional HTTP client.
    """

    def __init__(
        self,
        config: Optional[ExternalServicesConfig] = None,
        http_client: Optional[Any] = None,
    ):
        self.config = config or external_services_config
        self.http_client = http_client

    def lookup_trademark(self, brand_name: str) -> Dict[str, Any]:
        if not brand_name or not str(brand_name).strip():
            raise ExternalServiceInvalidInputError("brand_name must not be empty.")

        brand_clean = brand_name.strip()
        logger.info(f"Looking up trademark status for brand: '{brand_clean}'.")

        if self.http_client is not None:
            url = f"{self.config.BRAND_REGISTRY_API_URL}/trademarks/{brand_clean}"
            try:
                response = self.http_client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.config.BRAND_REGISTRY_API_KEY}"
                    },
                    timeout=self.config.BRAND_REGISTRY_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout checking trademark for '{brand_clean}'."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error looking up trademark for '{brand_clean}': {e}"
                ) from e

        # Mock response simulation
        registered_brands = [
            "nike",
            "apple",
            "rolex",
            "gucci",
            "louis vuitton",
            "sony",
            "adidas",
        ]
        is_registered = (
            brand_clean.lower() in registered_brands or len(brand_clean) >= 4
        )

        if is_registered:
            return {
                "brand_name": brand_clean,
                "is_registered": True,
                "status": "ACTIVE",
                "registration_number": f"TM-GLOBAL-{len(brand_clean) * 9871}",
                "owner_entity": f"{brand_clean.title()} IP Holdings Ltd.",
                "jurisdiction": "International (WIPO/USPTO/EUIPO)",
                "source": "mock_brand_registry_wrapper",
            }
        else:
            return {
                "brand_name": brand_clean,
                "is_registered": False,
                "status": "UNREGISTERED",
                "registration_number": None,
                "owner_entity": None,
                "source": "mock_brand_registry_wrapper",
            }

    def verify_reseller(self, brand_name: str, seller_name: str) -> Dict[str, Any]:
        if not brand_name or not str(brand_name).strip():
            raise ExternalServiceInvalidInputError("brand_name must not be empty.")
        if not seller_name or not str(seller_name).strip():
            raise ExternalServiceInvalidInputError("seller_name must not be empty.")

        brand_clean = brand_name.strip()
        seller_clean = seller_name.strip()
        logger.info(
            f"Verifying reseller '{seller_clean}' authorization under brand '{brand_clean}'."
        )

        if self.http_client is not None:
            url = f"{self.config.BRAND_REGISTRY_API_URL}/resellers/verify"
            params = {"brand": brand_clean, "seller": seller_clean}
            try:
                response = self.http_client.get(
                    url,
                    params=params,
                    headers={
                        "Authorization": f"Bearer {self.config.BRAND_REGISTRY_API_KEY}"
                    },
                    timeout=self.config.BRAND_REGISTRY_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout verifying reseller '{seller_clean}'."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error verifying reseller '{seller_clean}': {e}"
                ) from e

        # Mock response simulation
        is_unauthorized = any(
            kw in seller_clean.lower()
            for kw in [
                "unauthorized",
                "fake",
                "replica",
                "discount",
                "cheap",
                "unverified",
            ]
        )

        return {
            "brand_name": brand_clean,
            "seller_name": seller_clean,
            "is_authorized_reseller": not is_unauthorized,
            "authorization_level": (
                "Official Distributor" if not is_unauthorized else "None (Unauthorized)"
            ),
            "verification_confidence": 0.99 if not is_unauthorized else 0.95,
            "source": "mock_brand_registry_wrapper",
        }

    def check_catalog(self, brand_name: str, product_title: str) -> Dict[str, Any]:
        if not brand_name or not str(brand_name).strip():
            raise ExternalServiceInvalidInputError("brand_name must not be empty.")
        if not product_title or not str(product_title).strip():
            raise ExternalServiceInvalidInputError("product_title must not be empty.")

        brand_clean = brand_name.strip()
        title_clean = product_title.strip()
        logger.info(
            f"Checking official catalog of '{brand_clean}' for product: '{title_clean}'."
        )

        if self.http_client is not None:
            url = f"{self.config.BRAND_REGISTRY_API_URL}/catalog/check"
            params = {"brand": brand_clean, "title": title_clean}
            try:
                response = self.http_client.get(
                    url,
                    params=params,
                    headers={
                        "Authorization": f"Bearer {self.config.BRAND_REGISTRY_API_KEY}"
                    },
                    timeout=self.config.BRAND_REGISTRY_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    return response.json()
                elif isinstance(response, dict):
                    return response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    "Timeout checking manufacturer catalog."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error checking catalog for product '{title_clean}': {e}"
                ) from e

        # Mock response simulation
        in_catalog = (
            "fake" not in title_clean.lower() and "replica" not in title_clean.lower()
        )
        return {
            "brand_name": brand_clean,
            "product_title": title_clean,
            "in_catalog": in_catalog,
            "expected_materials": "Premium Leather, Sapphire Glass, Stainless Steel"
            if in_catalog
            else "Unknown",
            "release_year": 2024 if in_catalog else None,
            "catalog_id": f"CAT-{len(title_clean) * 441}" if in_catalog else None,
            "source": "mock_brand_registry_wrapper",
        }
