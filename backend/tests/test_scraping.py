from unittest.mock import MagicMock, patch

import pytest
import requests

from backend.agents.analyzer import AnalyzerAgent
from backend.agents.collector import EvidenceCollector
from backend.schemas.investigation import InvestigationRequest
from backend.schemas.scraping import ParsedListing, ScrapingResult
from backend.scrapers.generic_parser import GenericParser
from backend.scrapers.page_fetcher import PageFetcher
from backend.services.investigation_service import InvestigationService
from backend.services.scraping_service import ScrapingService


def test_page_fetcher_success():
    fetcher = PageFetcher()
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        html = fetcher.fetch("http://test.com")
        assert html == "<html><body>Test</body></html>"
        mock_get.assert_called_once()


def test_page_fetcher_failure():
    fetcher = PageFetcher()
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_resp)
        with pytest.raises(Exception):
            fetcher.fetch("http://test.com")


def test_html_parser_extracts_data():
    parser = GenericParser()
    sample_html = """
    <html>
        <head>
            <title>Fake Rolex Watch</title>
            <meta property="og:image" content="https://images.example.com/rolex.jpg">
        </head>
        <body>
            <div id="price">$99.99</div>
            <span class="seller">Sold by ShadySeller123</span>
            <div>Rating: 2.5 out of 5 stars</div>
            <div>Brand: <span>FakeBrand</span></div>
            <img src="img1.jpg" width="100"/>
            <img src="img2.jpg" width="100"/>
            <div class="product-description">A very real looking watch.</div>
            <span>In stock</span>
            <div>No warranty provided</div>
        </body>
    </html>
    """
    listing = parser.parse(sample_html, "https://www.fakemarket.com/item/1")

    assert listing.title == "Fake Rolex Watch"
    assert listing.price == 99.99
    assert listing.seller_name == "ShadySeller123"
    assert listing.seller_rating == 2.5
    assert listing.brand == "FakeBrand"
    assert listing.images_count == 2
    assert listing.image_url == "https://images.example.com/rolex.jpg"
    assert listing.description == "A very real looking watch."
    assert listing.availability == "In stock"
    assert listing.warranty_info == "No warranty provided"
    assert listing.marketplace == "fakemarket.com"


def test_evidence_summary_honest_on_fallback():
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    req = InvestigationRequest(
        listing_url="http://example.com/item", marketplace="Global"
    )

    fallback_result = ScrapingResult(
        success=True,
        listing=ParsedListing(
            title="Fallback Item",
            price=149.99,
            seller_name="Global Merchant",
            brand="Generic Brand",
            marketplace="Global",
            data_source="fallback_demo_data",
        ),
    )

    analysis = analyzer.analyze(req, fallback_result)
    evidence = collector.collect(analysis, fallback_result)
    se = evidence.structured_evidence

    for field, data in se.items():
        assert (
            data["status"] == "Unavailable"
        ), f"Field '{field}' status must be 'Unavailable', got '{data['status']}'"
        assert data["reason"] == "No live data retrieved"


def test_seller_name_extraction():
    """
    ISSUE 2 Test: Verifies correct seller_name extraction against each of the 3 demo HTML fixtures.
    """
    service = ScrapingService(demo_mode=True)

    expected = [
        ("demo://genuine", "Sony Direct Store"),
        ("demo://counterfeit", "Discount Replica Outlet"),
        ("demo://suspicious", "ElectroDeals Direct"),
    ]

    for url, expected_seller in expected:
        res = service.scrape(url)
        assert res.success is True
        assert (
            res.listing.seller_name == expected_seller
        ), f"Expected '{expected_seller}', got '{res.listing.seller_name}'"


def test_suspicious_demo_scoring():
    """
    ISSUE 1 Test: Asserts demo://suspicious risk_level is MEDIUM or higher given its findings,
    and ai_summary never claims '0 risk signals' when findings are present.
    """
    service = InvestigationService()
    req = InvestigationRequest(
        listing_url="demo://suspicious",
        product_name="Sony WH-1000XM5 Wireless Headphones",
        marketplace="ElectroDeals Direct",
    )

    report = service.run_investigation(req)

    assert report.risk_level in (
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ), f"Expected MEDIUM/HIGH/CRITICAL risk level, got '{report.risk_level}'"
    assert (
        report.risk_score >= 25
    ), f"Expected risk_score >= 25, got {report.risk_score}"
    assert "0 risk signals detected" not in report.ai_summary.lower()
    assert report.seller == "ElectroDeals Direct"


def test_confidence_differs_across_scenarios():
    """
    ISSUE 3 Test: Asserts confidence differs meaningfully across the 3 demo scenarios.
    """
    service = InvestigationService()

    rep_genuine = service.run_investigation(
        InvestigationRequest(
            listing_url="demo://genuine",
            product_name="Sony WH-1000XM5",
            marketplace="Sony Direct",
        )
    )
    rep_counterfeit = service.run_investigation(
        InvestigationRequest(
            listing_url="demo://counterfeit",
            product_name="Sony WH-1000XM5 Replica",
            marketplace="Discount Replica Outlet",
        )
    )
    rep_suspicious = service.run_investigation(
        InvestigationRequest(
            listing_url="demo://suspicious",
            product_name="Sony WH-1000XM5 Deals",
            marketplace="ElectroDeals Direct",
        )
    )

    conf_g = rep_genuine.confidence
    conf_c = rep_counterfeit.confidence
    conf_s = rep_suspicious.confidence

    assert (
        conf_g != conf_s or conf_c != conf_s
    ), f"Confidence scores must differ across scenarios. Got genuine={conf_g}, counterfeit={conf_c}, suspicious={conf_s}"
    assert not (
        conf_g == conf_c == conf_s == 0.7772
    ), "Confidence score must not be hardcoded to 0.7772"
