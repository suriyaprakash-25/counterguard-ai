from typing import Optional

from pydantic_settings import BaseSettings


class ExternalServicesConfig(BaseSettings):
    """
    Configuration settings for external third-party service wrappers
    (Marketplace API, Google Search, Brand Registry, Exchange Rate, and WHOIS).
    """

    # Marketplace API Config
    MARKETPLACE_API_BASE_URL: str = "https://api.marketplace.example.com/v1"
    MARKETPLACE_API_KEY: Optional[str] = "mock_marketplace_key"
    MARKETPLACE_TIMEOUT_SECONDS: int = 10
    MARKETPLACE_MAX_RETRIES: int = 3

    # Google Search Config
    GOOGLE_SEARCH_API_URL: str = "https://www.googleapis.com/customsearch/v1"
    GOOGLE_SEARCH_API_KEY: Optional[str] = "mock_google_key"
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = "mock_cx_id"
    GOOGLE_SEARCH_TIMEOUT_SECONDS: int = 10

    # Brand Registry Config
    BRAND_REGISTRY_API_URL: str = "https://api.brandregistry.example.com/v2"
    BRAND_REGISTRY_API_KEY: Optional[str] = "mock_brand_registry_key"
    BRAND_REGISTRY_TIMEOUT_SECONDS: int = 15

    # Exchange Rate Config
    EXCHANGE_RATE_API_URL: str = "https://api.exchangerate.example.com/latest"
    EXCHANGE_RATE_API_KEY: Optional[str] = "mock_exchange_rate_key"
    EXCHANGE_RATE_DEFAULT_BASE_CURRENCY: str = "USD"
    EXCHANGE_RATE_TIMEOUT_SECONDS: int = 5

    # WHOIS Config
    WHOIS_API_URL: str = "https://api.whois.example.com/v1"
    WHOIS_API_KEY: Optional[str] = "mock_whois_key"
    WHOIS_TIMEOUT_SECONDS: int = 10
    WHOIS_CACHE_ENABLED: bool = True
    WHOIS_CACHE_TTL_SECONDS: int = 86400

    model_config = {
        "env_prefix": "COUNTERGUARD_EXTERNAL_",
        "case_sensitive": True,
        "extra": "ignore",
    }


external_services_config = ExternalServicesConfig()
