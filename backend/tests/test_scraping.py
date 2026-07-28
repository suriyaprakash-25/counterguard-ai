from unittest.mock import MagicMock, patch

import pytest
import requests

from backend.agents.analyzer import AnalyzerAgent
from backend.agents.collector import EvidenceCollector
from backend.schemas.investigation import InvestigationRequest
from backend.schemas.scraping import ParsedListing, ScrapingResult
from backend.scrapers.generic_parser import GenericParser
from backend.scrapers.page_fetcher import PageFetcher
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
    """
    FIX 1 Test: Asserts that if data_source is fallback_demo_data,
    no evidence_summary field may report any status other than 'Unavailable'.
    """
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


def test_demo_mode_snapshots():
    """
    FIX 2 Test: Verifies DEMO_MODE loads pre-fetched HTML snapshots,
    executes real parser code, populates image_url, and returns valid data_source.
    """
    service = ScrapingService(demo_mode=True)

    cases = [
        ("demo://genuine", "Sony WH-1000XM5", 399.99),
        ("demo://counterfeit", "Original Sony WH-1000XM5", 39.99),
        ("demo://suspicious", "Sony WH-1000XM5", 189.99),
    ]

    for url, title_substr, expected_price in cases:
        res = service.scrape(url)
        assert res.success is True
        assert res.listing is not None
        assert title_substr in res.listing.title
        assert res.listing.price == expected_price
        assert res.listing.image_url is not None
        assert res.listing.image_url.startswith("https://images.unsplash.com")
        assert res.listing.data_source == "live_retrieval"
