"""
CounterGuard External Service Wrappers.

Provides abstractions and concrete implementations for third-party intelligence sources:
Marketplace API, Google Search OSINT, Brand Registry, Exchange Rates, and WHOIS registries.
All implementations support constructor dependency injection and structured mock response simulation.
"""

from backend.services.external.brand_registry import BrandRegistryWrapper
from backend.services.external.exceptions import (
    ExternalServiceError,
    ExternalServiceInvalidInputError,
    ExternalServiceTimeoutError,
    ExternalServiceUnavailableError,
)
from backend.services.external.exchange_rate import ExchangeRateWrapper
from backend.services.external.google_search import GoogleSearchWrapper
from backend.services.external.interfaces import (
    BrandRegistryWrapperInterface,
    ExchangeRateWrapperInterface,
    GoogleSearchWrapperInterface,
    MarketplaceAPIWrapperInterface,
    WhoisWrapperInterface,
)
from backend.services.external.marketplace import MarketplaceAPIWrapper
from backend.services.external.whois_lookup import WhoisWrapper

__all__ = [
    # Interfaces
    "MarketplaceAPIWrapperInterface",
    "GoogleSearchWrapperInterface",
    "BrandRegistryWrapperInterface",
    "ExchangeRateWrapperInterface",
    "WhoisWrapperInterface",
    # Concrete Wrappers
    "MarketplaceAPIWrapper",
    "GoogleSearchWrapper",
    "BrandRegistryWrapper",
    "ExchangeRateWrapper",
    "WhoisWrapper",
    # Exceptions
    "ExternalServiceError",
    "ExternalServiceTimeoutError",
    "ExternalServiceUnavailableError",
    "ExternalServiceInvalidInputError",
]
