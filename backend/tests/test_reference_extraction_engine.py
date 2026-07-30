from backend.extractors.price_extractor import PriceExtractor
from backend.extractors.title_extractor import TitleExtractor
from backend.providers.extraction.html_provider import HTMLExtractionProvider
from backend.providers.extraction.jsonld_provider import JsonLdExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.raw_extraction import RawExtractionResult
from backend.services.extraction_normalization_engine import (
    ExtractionNormalizationEngine,
)
from backend.services.extraction_validation_engine import ExtractionValidationEngine
from backend.services.reference_extraction_service import ReferenceExtractionService


def test_field_extractors_and_evidence_trail():
    cand = SourceCandidate(
        title="CMF Buds Pro",
        url="https://nothing.tech/products/cmf-buds-pro",
        provider="StaticBrandProvider",
        domain="nothing.tech",
        confidence=0.98,
        metadata={"raw_price_str": "Rs. 3,499", "brand_key": "Nothing"},
    )

    t_ext = TitleExtractor()
    title_val, title_ev = t_ext.extract_field(cand)
    assert title_val == "CMF Buds Pro"
    assert title_ev.field == "title"
    assert title_ev.source_url == cand.url
    assert "h1" in title_ev.css_selector

    p_ext = PriceExtractor()
    price_val, price_ev = p_ext.extract_field(cand)
    assert price_val == "Rs. 3,499"
    assert price_ev.field == "price"
    assert "price" in price_ev.css_selector


def test_raw_extraction_result_schema():
    raw = RawExtractionResult(
        url="https://nothing.tech/products/cmf-buds",
        provider="HTMLExtractionProvider",
        raw_title="CMF Buds by Nothing",
        raw_brand="Nothing",
        raw_price_str="Rs. 2,499",
        raw_specs={"Battery Capacity": "45 mAh", "Noise Cancellation": "42dB"},
        extraction_method="html",
        confidence=0.95,
    )

    assert raw.url == "https://nothing.tech/products/cmf-buds"
    assert raw.raw_price_str == "Rs. 2,499"
    assert raw.raw_specs["Battery Capacity"] == "45 mAh"
    assert raw.confidence == 0.95


def test_extraction_normalization_engine():
    normalizer = ExtractionNormalizationEngine()

    val1, curr1 = normalizer.parse_price("$199.99")
    assert val1 == 199.99
    assert curr1 == "USD"

    val2, curr2 = normalizer.parse_price("Rs. 4,999")
    assert val2 == 4999.0
    assert curr2 == "INR"

    raw = RawExtractionResult(
        url="https://apple.com/airpods-pro",
        provider="JsonLdExtractionProvider",
        raw_title="AirPods Pro (2nd gen)",
        raw_brand="Apple",
        raw_price_str="$249.00",
        raw_specs={"Battery Capacity": "45 mAh", "Weight": "5.3 grams"},
        confidence=0.98,
    )

    profile = normalizer.normalize(raw)
    assert profile.brand == "Apple"
    assert profile.product_name == "AirPods Pro (2nd gen)"
    assert profile.msrp == 249.0
    assert profile.currency == "USD"
    assert profile.specifications["battery_capacity"] == "45 mAh"


def test_extraction_validation_engine():
    validator = ExtractionValidationEngine()

    raw = RawExtractionResult(
        url="https://apple.com/airpods-pro",
        provider="JsonLdExtractionProvider",
        raw_title="AirPods Pro",
        raw_brand="Apple",
        confidence=0.95,
    )
    normalizer = ExtractionNormalizationEngine()
    profile = normalizer.normalize(raw)

    is_valid, reason = validator.validate(profile)
    assert is_valid is True
    assert "Validated" in reason


def test_reference_extraction_service_strategy_selection():
    service = ReferenceExtractionService()

    cand_jsonld = SourceCandidate(
        title="Nike Air Force 1",
        url="https://nike.com/shoes/af1",
        provider="StaticBrandProvider",
        domain="nike.com",
        confidence=0.98,
    )

    cand_html = SourceCandidate(
        title="Generic Headphones",
        url="https://generic-store.com/item",
        provider="StaticBrandProvider",
        domain="generic-store.com",
        confidence=0.80,
    )

    prov1 = service.select_provider(cand_jsonld)
    assert isinstance(prov1, JsonLdExtractionProvider)

    prov2 = service.select_provider(cand_html)
    assert isinstance(prov2, HTMLExtractionProvider)


def test_reference_extraction_service_end_to_end_with_evidence():
    service = ReferenceExtractionService()

    candidate = SourceCandidate(
        title="Nothing Phone (2a)",
        url="https://nothing.tech/products/phone-2a",
        provider="StaticBrandProvider",
        domain="nothing.tech",
        confidence=0.98,
        metadata={"brand_key": "Nothing", "raw_price_str": "Rs. 23,999"},
    )

    raw_result, profile, is_valid = service.extract_profile(candidate)

    assert raw_result.url == "https://nothing.tech/products/phone-2a"
    assert profile.product_name == "Nothing Phone (2a)"
    assert profile.brand == "Nothing"
    assert is_valid is True

    # Assert evidence trail contains field traceability
    assert len(raw_result.evidence_trail) >= 2
    assert len(profile.evidence_trail) >= 2
    fields_traced = [ev.field for ev in profile.evidence_trail]
    assert "title" in fields_traced
    assert "price" in fields_traced
