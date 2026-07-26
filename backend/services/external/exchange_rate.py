import logging
from datetime import datetime, timezone
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
from backend.services.external.interfaces import ExchangeRateWrapperInterface

logger = logging.getLogger(__name__)


class ExchangeRateWrapper(ExchangeRateWrapperInterface):
    """
    Concrete service wrapper for foreign currency Exchange Rate feeds.
    Supports constructor dependency injection for configuration and optional HTTP client.
    """

    def __init__(
        self,
        config: Optional[ExternalServicesConfig] = None,
        http_client: Optional[Any] = None,
    ):
        self.config = config or external_services_config
        self.http_client = http_client

    def get_rate(
        self, target_currency: str, base_currency: Optional[str] = None
    ) -> float:
        if not target_currency or not str(target_currency).strip():
            raise ExternalServiceInvalidInputError("target_currency must not be empty.")

        base = (
            base_currency.upper().strip()
            if base_currency
            else self.config.EXCHANGE_RATE_DEFAULT_BASE_CURRENCY
        )
        target = target_currency.upper().strip()

        if base == target:
            return 1.0

        logger.info(f"Retrieving foreign exchange rate: {base} -> {target}.")

        if self.http_client is not None:
            params = {
                "access_key": self.config.EXCHANGE_RATE_API_KEY,
                "base": base,
                "symbols": target,
            }
            try:
                response = self.http_client.get(
                    self.config.EXCHANGE_RATE_API_URL,
                    params=params,
                    timeout=self.config.EXCHANGE_RATE_TIMEOUT_SECONDS,
                )
                if hasattr(response, "json"):
                    data = response.json()
                elif isinstance(response, dict):
                    data = response
                else:
                    data = {}

                if "rates" in data and target in data["rates"]:
                    return float(data["rates"][target])
            except TimeoutError as e:
                raise ExternalServiceTimeoutError(
                    f"Timeout fetching rate for {base} -> {target}."
                ) from e
            except Exception as e:
                raise ExternalServiceError(
                    f"Error communicating with Exchange Rate API: {e}"
                ) from e

        # Mock exchange rate matrix (relative to USD)
        usd_rates: Dict[str, float] = {
            "USD": 1.00,
            "EUR": 0.92,
            "GBP": 0.79,
            "CNY": 7.23,
            "JPY": 155.40,
            "CAD": 1.36,
            "AUD": 1.51,
            "INR": 83.50,
            "CHF": 0.89,
            "SGD": 1.35,
        }

        base_rate = usd_rates.get(base, 1.0)
        target_rate = usd_rates.get(target, 1.25)
        computed_rate = round(target_rate / base_rate, 6)
        return computed_rate

    def convert(
        self, amount: float, target_currency: str, base_currency: Optional[str] = None
    ) -> Dict[str, Any]:
        if not target_currency or not str(target_currency).strip():
            raise ExternalServiceInvalidInputError("target_currency must not be empty.")
        if amount < 0:
            raise ExternalServiceInvalidInputError("Amount cannot be negative.")

        base = (
            base_currency.upper().strip()
            if base_currency
            else self.config.EXCHANGE_RATE_DEFAULT_BASE_CURRENCY
        )
        target = target_currency.upper().strip()

        rate = self.get_rate(target_currency=target, base_currency=base)
        converted_amount = round(amount * rate, 2)

        return {
            "base_currency": base,
            "target_currency": target,
            "rate": rate,
            "original_amount": float(amount),
            "converted_amount": converted_amount,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "source": "mock_exchange_rate_wrapper",
        }
