from unittest.mock import MagicMock, patch

import pytest
import requests

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
        <head><title>Fake Rolex Watch</title></head>
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
    assert listing.description == "A very real looking watch."
    assert listing.availability == "In stock"
    assert listing.warranty_info == "No warranty provided"
    assert listing.marketplace == "fakemarket.com"


def test_scraping_service():
    service = ScrapingService()
    with patch.object(service.fetcher, "fetch") as mock_fetch:
        mock_fetch.return_value = (
            "<html><body><h1>Item</h1><div id='price'>$5.00</div></body></html>"
        )

        result = service.scrape("https://test.com/item")
        assert result.success is True
        assert result.listing.title == "Item"
        assert result.listing.price == 5.0

    with patch.object(service.fetcher, "fetch") as mock_fetch:
        mock_fetch.side_effect = Exception("Connection Failed")

        result = service.scrape("https://test.com/item")
        assert result.success is False
        assert result.error_message == "Connection Failed"
