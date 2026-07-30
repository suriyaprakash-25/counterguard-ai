from backend.extractors.price_extractor import PriceExtractor
from backend.extractors.title_extractor import TitleExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.raw_extraction import RawExtractionResult
from backend.services.canonical_knowledge_builder import CanonicalKnowledgeBuilder
from backend.services.extraction_normalization_engine import (
    ExtractionNormalizationEngine,
)
from backend.services.extraction_orchestrator import ExtractionOrchestrator
from backend.services.reference_extraction_service import ReferenceExtractionService


def test_canonical_knowledge_builder():
    normalizer = ExtractionNormalizationEngine()
    builder = CanonicalKnowledgeBuilder()

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

    profile = normalizer.normalize(raw)
    canonical = builder.build_from_profile(profile)

    assert canonical.brand == "Nothing"
    assert canonical.product_name == "CMF Buds by Nothing"
    assert canonical.canonical_id == "nothing-cmf-buds-by-nothing"
    assert canonical.msrp == 2499.0
    assert canonical.currency == "INR"
    assert canonical.canonical_specs["battery_capacity"] == "45 mAh"


def test_extraction_orchestrator_cascade():
    orchestrator = ExtractionOrchestrator()

    cand = SourceCandidate(
        title="Nike Air Jordan 1",
        url="https://nike.com/shoes/aj1",
        provider="StaticBrandProvider",
        domain="nike.com",
        confidence=0.98,
    )

    raw, profile, is_valid = orchestrator.execute_extraction_cascade(cand)
    assert raw.provider == "JsonLdExtractionProvider"
    assert profile.brand == "Nike"
    assert is_valid is True


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


def test_reference_extraction_service_canonical_knowledge():
    service = ReferenceExtractionService()

    candidate = SourceCandidate(
        title="Nothing Phone (2a)",
        url="https://nothing.tech/products/phone-2a",
        provider="StaticBrandProvider",
        domain="nothing.tech",
        confidence=0.98,
        metadata={"brand_key": "Nothing", "raw_price_str": "Rs. 23,999"},
    )

    knowledge, is_valid = service.extract_canonical_knowledge(candidate)

    assert knowledge.product_name == "Nothing Phone (2a)"
    assert knowledge.brand == "Nothing"
    assert knowledge.canonical_id == "nothing-nothing-phone-2a"
    assert knowledge.msrp == 23999.0
    assert is_valid is True
    assert len(knowledge.evidence_trail) >= 2
