import logging
from datetime import datetime, timedelta, timezone
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
from backend.services.external.interfaces import WhoisWrapperInterface

logger = logging.getLogger(__name__)


class WhoisWrapper(WhoisWrapperInterface):
    """
    Concrete service wrapper for WHOIS domain registry intelligence.
    Supports constructor dependency injection for configuration, optional HTTP client, and cache backend.
    """

    def __init__(
        self,
        config: Optional[ExternalServicesConfig] = None,
        http_client: Optional[Any] = None,
        cache_backend: Optional[Dict[str, Any]] = None,
    ):
        self.config = config or external_services_config
        self.http_client = http_client
        self.cache = cache_backend if cache_backend is not None else {}

    def lookup_domain(self, domain: str) -> Dict[str, Any]:
        if not domain or not str(domain).strip():
            raise ExternalServiceInvalidInputError("Domain name must not be empty.")

        domain_clean = domain.lower().strip()
        logger.info(
            f"Performing WHOIS intelligence lookup for domain: '{domain_clean}'."
        )

        if self.config.WHOIS_CACHE_ENABLED and domain_clean in self.cache:
            logger.debug(f"Cache hit for domain '{domain_clean}'.")
            cached_result = self.cache[domain_clean]
            cached_result["cached"] = True
            return cached_result

        result: Optional[Dict[str, Any]] = None
        if self.http_client is not None:
            url = f"{self.config.WHOIS_API_URL}/lookup"
            params = {"domain": domain_clean, "apiKey": self.config.WHOIS_API_KEY}
            try:
                response = self.http_client.get(
                    url,
                    params=params,
                    timeout=self.config.WHOIS_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    result = response.json()
                elif isinstance(response, dict):
                    result = response
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout executing WHOIS lookup for '{domain_clean}'."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error performing WHOIS query for '{domain_clean}': {e}"
                ) from e

        if result is None:
            # Mock response simulation
            trusted_domains = [
                "amazon.com",
                "ebay.com",
                "nike.com",
                "apple.com",
                "walmart.com",
            ]
            is_trusted = any(td in domain_clean for td in trusted_domains)

            domain_age = 5400 if is_trusted else 18
            registrar = (
                "MarkMonitor, Inc."
                if is_trusted
                else "CheapNames Anonymous Registrar LLC"
            )
            is_private = not is_trusted

            creation_date = (
                datetime.now(timezone.utc) - timedelta(days=domain_age)
            ).strftime("%Y-%m-%d")

            result = {
                "domain": domain_clean,
                "domain_age_days": domain_age,
                "registrar": registrar,
                "is_private": is_private,
                "creation_date": creation_date,
                "status": ["clientTransferProhibited", "serverUpdateProhibited"]
                if is_trusted
                else ["active"],
                "risk_score": 0.05 if is_trusted else 0.88,
                "cached": False,
                "source": "mock_whois_wrapper",
            }

        if self.config.WHOIS_CACHE_ENABLED:
            self.cache[domain_clean] = result

        return result

    def get_registrar_info(self, domain: str) -> Dict[str, Any]:
        if not domain or not str(domain).strip():
            raise ExternalServiceInvalidInputError("Domain name must not be empty.")

        lookup_data = self.lookup_domain(domain)
        registrar_name = lookup_data.get("registrar", "Unknown Registrar")
        is_private = lookup_data.get("is_private", True)

        return {
            "domain": lookup_data["domain"],
            "registrar_name": registrar_name,
            "abuse_email": f"abuse@{registrar_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com",
            "whois_server": f"whois.{lookup_data['domain']}",
            "privacy_protection_enabled": is_private,
        }
