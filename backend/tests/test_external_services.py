from unittest import mock

import pytest

from backend.config import ExternalServicesConfig
from backend.services.external import (
    BrandRegistryWrapper,
    BrandRegistryWrapperInterface,
    ExchangeRateWrapper,
    ExchangeRateWrapperInterface,
    ExternalServiceError,
    ExternalServiceInvalidInputError,
    ExternalServiceTimeoutError,
    GoogleSearchWrapper,
    GoogleSearchWrapperInterface,
    MarketplaceAPIWrapper,
    MarketplaceAPIWrapperInterface,
    WhoisWrapper,
    WhoisWrapperInterface,
)


def test_interfaces_cannot_be_instantiated():
    with pytest.raises(TypeError):
        MarketplaceAPIWrapperInterface()
    with pytest.raises(TypeError):
        GoogleSearchWrapperInterface()
    with pytest.raises(TypeError):
        BrandRegistryWrapperInterface()
    with pytest.raises(TypeError):
        ExchangeRateWrapperInterface()
    with pytest.raises(TypeError):
        WhoisWrapperInterface()


def test_external_services_config_defaults_and_override():
    config = ExternalServicesConfig(
        MARKETPLACE_API_BASE_URL="https://custom.api.test",
        WHOIS_CACHE_ENABLED=False,
    )
    assert config.MARKETPLACE_API_BASE_URL == "https://custom.api.test"
    assert config.WHOIS_CACHE_ENABLED is False
    assert config.EXCHANGE_RATE_DEFAULT_BASE_CURRENCY == "USD"


# -------------------------------------------------------------------------
# Marketplace API Wrapper Tests
# -------------------------------------------------------------------------
def test_marketplace_wrapper_mock_responses():
    wrapper = MarketplaceAPIWrapper()

    # Normal listing
    res = wrapper.get_listing_details("B08N5WRWNW", marketplace="amazon")
    assert res["listing_id"] == "B08N5WRWNW"
    assert res["marketplace"] == "amazon"
    assert res["current_price"] == 199.99
    assert res["flags"] == []

    # Suspicious listing
    suspicious_res = wrapper.get_listing_details(
        "SUSPICIOUS_ITEM_001", marketplace="eBay"
    )
    assert "potential_counterfeit" in suspicious_res["flags"]
    assert suspicious_res["current_price"] == 39.99

    # Seller reputation
    rep = wrapper.get_seller_reputation("VERIFIED_SHOP")
    assert rep["verified_merchant"] is True
    assert rep["trust_score"] > 90

    unverified_rep = wrapper.get_seller_reputation("UNVERIFIED_FAKE_MERCHANT")
    assert unverified_rep["verified_merchant"] is False
    assert unverified_rep["trust_score"] < 50

    # Verify pricing
    price_check = wrapper.verify_pricing("B08N5WRWNW", current_price=45.00)
    assert price_check["price_anomaly_detected"] is True
    assert price_check["risk_level"] == "HIGH"


def test_marketplace_wrapper_dependency_injection_and_errors():
    mock_client = mock.MagicMock()
    mock_client.get.return_value = {"listing_id": "INJECTED", "status": "custom"}

    custom_config = ExternalServicesConfig(MARKETPLACE_TIMEOUT_SECONDS=5)
    wrapper = MarketplaceAPIWrapper(config=custom_config, http_client=mock_client)

    res = wrapper.get_listing_details("INJECTED")
    assert res["listing_id"] == "INJECTED"
    assert res["status"] == "custom"
    mock_client.get.assert_called_once()

    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.get_listing_details("")
    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.verify_pricing("ID", current_price=-10.0)

    # Simulate network failure
    mock_client.get.side_effect = TimeoutError("Connection timed out")
    with pytest.raises(ExternalServiceTimeoutError):
        wrapper.get_seller_reputation("TIMEOUT_SELLER")

    mock_client.get.side_effect = Exception("General connection reset")
    with pytest.raises(ExternalServiceError):
        wrapper.get_seller_reputation("FAIL_SELLER")


# -------------------------------------------------------------------------
# Google Search Wrapper Tests
# -------------------------------------------------------------------------
def test_google_search_wrapper_mock_responses():
    wrapper = GoogleSearchWrapper()

    # Web search
    web_res = wrapper.search_web("Nike Air Jordan 1 verification", num_results=2)
    assert web_res["query"] == "Nike Air Jordan 1 verification"
    assert len(web_res["results"]) == 2
    assert web_res["results"][0]["rank"] == 1

    # Reverse image search
    img_res = wrapper.search_images(
        "https://example.com/shoe_original.jpg", similarity_threshold=0.85
    )
    assert img_res["queried_image_url"] == "https://example.com/shoe_original.jpg"
    assert img_res["stolen_image"] is False

    replica_res = wrapper.search_images(
        "https://example.com/fake_shoe_copy.jpg", similarity_threshold=0.80
    )
    assert replica_res["stolen_image"] is True
    assert len(replica_res["matches"]) >= 1


def test_google_search_wrapper_dependency_injection_and_errors():
    mock_client = mock.MagicMock()
    mock_client.get.return_value = {"custom_search_result": True, "items": []}

    wrapper = GoogleSearchWrapper(http_client=mock_client)
    res = wrapper.search_web("custom test")
    assert res["custom_search_result"] is True

    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.search_web("   ")
    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.search_images("http://valid.url", similarity_threshold=1.5)


# -------------------------------------------------------------------------
# Brand Registry Wrapper Tests
# -------------------------------------------------------------------------
def test_brand_registry_wrapper_mock_responses():
    wrapper = BrandRegistryWrapper()

    # Trademark lookup
    tm_auth = wrapper.lookup_trademark("Nike")
    assert tm_auth["is_registered"] is True
    assert tm_auth["status"] == "ACTIVE"

    tm_unauth = wrapper.lookup_trademark("xyz")
    assert tm_unauth["is_registered"] is False

    # Reseller verification
    reseller_valid = wrapper.verify_reseller("Nike", "Official Nike Shop")
    assert reseller_valid["is_authorized_reseller"] is True

    reseller_fake = wrapper.verify_reseller(
        "Nike", "Unauthorized Discount Replica Shop"
    )
    assert reseller_fake["is_authorized_reseller"] is False
    assert "Unauthorized" in reseller_fake["authorization_level"]

    # Catalog check
    catalog_res = wrapper.check_catalog("Rolex", "Submariner Oystersteel")
    assert catalog_res["in_catalog"] is True
    assert "Sapphire Glass" in catalog_res["expected_materials"]

    catalog_fake = wrapper.check_catalog("Rolex", "Cheap Replica Rolex Watch")
    assert catalog_fake["in_catalog"] is False


def test_brand_registry_wrapper_errors_and_di():
    mock_client = mock.MagicMock()
    mock_client.get.return_value = {"in_catalog": True, "custom_injected": True}
    wrapper = BrandRegistryWrapper(http_client=mock_client)

    res = wrapper.check_catalog("TestBrand", "TestProduct")
    assert res["custom_injected"] is True

    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.lookup_trademark("")
    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.verify_reseller("Brand", "")


# -------------------------------------------------------------------------
# Exchange Rate Wrapper Tests
# -------------------------------------------------------------------------
def test_exchange_rate_wrapper_mock_responses():
    wrapper = ExchangeRateWrapper()

    rate_eur = wrapper.get_rate("EUR", base_currency="USD")
    assert rate_eur == 0.92

    same_rate = wrapper.get_rate("USD", base_currency="USD")
    assert same_rate == 1.0

    conv_res = wrapper.convert(100.0, "EUR", base_currency="USD")
    assert conv_res["converted_amount"] == 92.0
    assert conv_res["base_currency"] == "USD"
    assert conv_res["target_currency"] == "EUR"


def test_exchange_rate_wrapper_errors_and_di():
    mock_client = mock.MagicMock()
    mock_client.get.return_value = {"rates": {"CAD": 1.45}}
    wrapper = ExchangeRateWrapper(http_client=mock_client)

    assert wrapper.get_rate("CAD", "USD") == 1.45

    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.get_rate("")
    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.convert(-50.0, "EUR")


# -------------------------------------------------------------------------
# WHOIS Wrapper Tests
# -------------------------------------------------------------------------
def test_whois_wrapper_mock_responses_and_caching():
    cache_store = {}
    wrapper = WhoisWrapper(cache_backend=cache_store)

    # First lookup (should miss cache and populate it)
    auth_res = wrapper.lookup_domain("amazon.com")
    assert auth_res["domain"] == "amazon.com"
    assert auth_res["domain_age_days"] == 5400
    assert auth_res["cached"] is False
    assert "amazon.com" in cache_store

    # Second lookup (should hit cache)
    cached_res = wrapper.lookup_domain("amazon.com")
    assert cached_res["cached"] is True

    # Registrar info
    reg_info = wrapper.get_registrar_info("amazon.com")
    assert reg_info["whois_server"] == "whois.amazon.com"

    # Suspicious domain
    susp_res = wrapper.lookup_domain("newly-created-scam-shop.xy")
    assert susp_res["domain_age_days"] == 18
    assert susp_res["risk_score"] > 0.5


def test_whois_wrapper_di_and_errors():
    mock_client = mock.MagicMock()
    mock_client.get.return_value = {
        "domain": "custom-di.test",
        "cached": False,
        "domain_age_days": 100,
    }
    wrapper = WhoisWrapper(http_client=mock_client)

    res = wrapper.lookup_domain("custom-di.test")
    assert res["domain_age_days"] == 100

    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.lookup_domain("   ")
    with pytest.raises(ExternalServiceInvalidInputError):
        wrapper.get_registrar_info("")
