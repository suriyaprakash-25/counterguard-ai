from backend.providers.extraction.api_provider import StructuredApiExtractionProvider
from backend.providers.extraction.html_provider import HTMLExtractionProvider
from backend.providers.extraction.jsonld_provider import JsonLdExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.raw_extraction import RawExtractionResult
from backend.services.canonical_knowledge_builder import CanonicalKnowledgeBuilder
from backend.services.extraction_normalization_engine import (
    ExtractionNormalizationEngine,
)
from backend.services.extraction_orchestrator import ExtractionOrchestrator
from backend.services.extraction_validation_engine import ExtractionValidationEngine
from backend.services.reference_extraction_service import ReferenceExtractionService


def test_html_extraction_provider_with_mock_dom():
    provider = HTMLExtractionProvider()
    candidate = SourceCandidate(
        title="Nothing CMF Buds Pro 2",
        url="https://nothing.tech/products/cmf-buds-pro-2",
        provider="StaticBrandProvider",
        domain="nothing.tech",
        confidence=0.98,
    )
    raw_html = """
    <html>
        <head>
            <meta property="og:title" content="CMF Buds Pro 2 - Nothing Tech" />
            <meta property="og:image" content="https://nothing.tech/cdn/hero.png" />
            <meta property="og:price:amount" content="4299" />
            <meta property="og:price:currency" content="INR" />
        </head>
        <body>
            <h1>CMF Buds Pro 2 Wireless Earbuds</h1>
            <div class="price">₹4,299</div>
            <div class="warranty">1 Year Official Manufacturer Warranty</div>
            <table>
                <tr><th>Driver Size</th><td>11mm Dual Drivers</td></tr>
                <tr><th>Noise Cancellation</th><td>50dB Hybrid ANC</td></tr>
                <tr><th>Battery Capacity</th><td>60 mAh</td></tr>
            </table>
        </body>
    </html>
    """

    res = provider.extract(candidate, raw_html)
    assert res.raw_title == "CMF Buds Pro 2 - Nothing Tech"
    assert res.raw_price_str == "INR 4299"
    assert len(res.raw_images) >= 1
    assert res.raw_specs["driver_size"] == "11mm Dual Drivers"
    assert res.raw_specs["noise_cancellation"] == "50dB Hybrid ANC"
    assert len(res.evidence_trail) >= 3


def test_json_ld_extraction_provider():
    provider = JsonLdExtractionProvider()
    candidate = SourceCandidate(
        title="Apple AirPods Pro",
        url="https://apple.com/airpods-pro",
        provider="StaticBrandProvider",
        domain="apple.com",
        confidence=0.98,
    )
    raw_html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": "AirPods Pro (2nd Generation)",
                "image": ["https://apple.com/images/airpods.jpg"],
                "description": "Active Noise Cancellation audio earbuds.",
                "sku": "APP-2GEN",
                "brand": {"@type": "Brand", "name": "Apple"},
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "USD",
                    "price": "249.00"
                }
            }
            </script>
        </head>
    </html>
    """

    res = provider.extract(candidate, raw_html)
    assert res.raw_title == "AirPods Pro (2nd Generation)"
    assert res.raw_brand == "Apple"
    assert res.raw_price_str == "USD 249.00"
    assert res.raw_images == ["https://apple.com/images/airpods.jpg"]
    assert res.raw_specs["sku"] == "APP-2GEN"
    assert len(res.evidence_trail) >= 2


def test_structured_api_extraction_provider_next_data():
    provider = StructuredApiExtractionProvider()
    candidate = SourceCandidate(
        title="Sony WH-1000XM5",
        url="https://sony.com/headphones/wh1000xm5",
        provider="StaticBrandProvider",
        domain="sony.com",
        confidence=0.98,
    )
    raw_html = """
    <html>
        <body>
            <script id="__NEXT_DATA__" type="application/json">
            {
                "props": {
                    "pageProps": {
                        "product": {
                            "title": "Sony WH-1000XM5 Wireless Headphones",
                            "price": 29990,
                            "images": [{"src": "https://sony.com/img1.jpg"}],
                            "specs": {"battery_life": "30 Hours"}
                        }
                    }
                }
            }
            </script>
        </body>
    </html>
    """

    res = provider.extract(candidate, raw_html)
    assert res.raw_title == "Sony WH-1000XM5 Wireless Headphones"
    assert res.raw_price_str == "INR 29990"
    assert res.raw_images == ["https://sony.com/img1.jpg"]
    assert res.raw_specs["battery_life"] == "30 Hours"


def test_extraction_orchestrator_provider_fusion():
    orchestrator = ExtractionOrchestrator()
    candidate = SourceCandidate(
        title="Nike Air Force 1 '07",
        url="https://nike.com/shoes/air-force-1",
        provider="StaticBrandProvider",
        domain="nike.com",
        confidence=0.98,
    )
    # Mixed raw HTML containing both JSON-LD title and HTML spec table
    raw_html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": "Nike Air Force 1 '07 Official",
                "brand": "Nike",
                "offers": {"@type": "Offer", "price": "115.00", "priceCurrency": "USD"}
            }
            </script>
        </head>
        <body>
            <h1>Nike Air Force 1</h1>
            <table>
                <tr><th>Material</th><td>Genuine Leather</td></tr>
                <tr><th>Sole</th><td>Rubber Air Cushion</td></tr>
            </table>
        </body>
    </html>
    """

    raw_fused, profile, is_valid = orchestrator.execute_extraction_cascade(
        candidate, raw_html
    )
    assert is_valid is True
    assert profile.brand == "Nike"
    assert profile.product_name == "Nike Air Force 1 '07 Official"
    assert profile.msrp == 115.0
    assert profile.currency == "USD"
    assert profile.specifications["material"] == "Genuine Leather"
    assert profile.specifications["sole"] == "Rubber Air Cushion"
    assert profile.metadata["quality_score"] >= 0.8
    assert profile.metadata["validation_status"] == "valid"


def test_normalization_and_validation_engines():
    normalizer = ExtractionNormalizationEngine()
    validator = ExtractionValidationEngine()

    raw = RawExtractionResult(
        url="https://samsung.com/galaxy-s24",
        provider="JsonLdExtractionProvider",
        raw_title="Samsung Galaxy S24 Ultra",
        raw_brand="Samsung",
        raw_price_str="$1,299.99",
        raw_specs={
            "Battery Capacity": "5000 mAh",
            "Display Size": "6.8 inches",
            "Internal Memory": "512 GB",
        },
        raw_images=["https://samsung.com/s24.jpg"],
        confidence=0.98,
    )

    profile = normalizer.normalize(raw)
    assert profile.specifications["battery_capacity"] == "5000 mAh"
    assert profile.specifications["display_size"] == "6.8 inches"
    assert profile.specifications["storage"] == "512 GB"
    assert profile.msrp == 1299.99
    assert profile.currency == "USD"

    is_valid, reason = validator.validate(profile)
    assert is_valid is True
    assert profile.metadata["quality_score"] == 1.0
    assert profile.metadata["validation_status"] == "valid"


def test_canonical_knowledge_builder():
    normalizer = ExtractionNormalizationEngine()
    validator = ExtractionValidationEngine()
    builder = CanonicalKnowledgeBuilder()

    raw = RawExtractionResult(
        url="https://nothing.tech/products/cmf-phone-1",
        provider="HTMLExtractionProvider",
        raw_title="CMF Phone 1 by Nothing",
        raw_brand="Nothing",
        raw_price_str="Rs. 15,999",
        raw_specs={"Battery Size": "5000 mAh", "Processor": "MediaTek Dimensity 7300"},
        raw_images=["https://nothing.tech/phone1.jpg"],
        confidence=0.95,
    )

    profile = normalizer.normalize(raw)
    validator.validate(profile)

    auxiliary_sources = [
        {"source_name": "bis_certification_db"},
        {"source_name": "fcc_telecom_db"},
    ]
    knowledge = builder.build_from_profile(profile, auxiliary_sources=auxiliary_sources)

    assert knowledge.brand == "Nothing"
    assert knowledge.product_name == "CMF Phone 1 by Nothing"
    assert knowledge.canonical_id == "nothing-cmf-phone-1-by-nothing"
    assert knowledge.msrp == 15999.0
    assert knowledge.currency == "INR"
    assert profile.source in knowledge.provenance_sources
    assert "bis_certification_db" in knowledge.provenance_sources
    assert "fcc_telecom_db" in knowledge.provenance_sources


def test_reference_extraction_service_full_pipeline():
    service = ReferenceExtractionService()
    candidate = SourceCandidate(
        title="Sony WH-1000XM5",
        url="https://sony.com/headphones/wh1000xm5",
        provider="StaticBrandProvider",
        domain="sony.com",
        confidence=0.98,
        metadata={"raw_price_str": "$399.99"},
    )
    raw_html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": "Sony WH-1000XM5 Premium Noise Canceling Headphones",
                "brand": {"@type": "Brand", "name": "Sony"},
                "image": ["https://sony.com/xm5.jpg"],
                "offers": {"@type": "Offer", "price": "399.99", "priceCurrency": "USD"}
            }
            </script>
        </head>
        <body>
            <h1>Sony WH-1000XM5</h1>
            <table>
                <tr><th>Noise Cancellation</th><td>HD Noise Canceling Processor QN1</td></tr>
                <tr><th>Battery Life</th><td>30 Hours</td></tr>
            </table>
        </body>
    </html>
    """

    knowledge, is_valid = service.extract_canonical_knowledge(candidate, raw_html)

    assert is_valid is True
    assert knowledge.brand == "Sony"
    assert (
        knowledge.product_name == "Sony WH-1000XM5 Premium Noise Canceling Headphones"
    )
    assert knowledge.msrp == 399.99
    assert knowledge.currency == "USD"
    assert knowledge.canonical_specs["battery_life"] == "30 Hours"
    assert len(knowledge.evidence_trail) >= 2
