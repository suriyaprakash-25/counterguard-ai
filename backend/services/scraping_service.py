import logging

from backend.schemas.scraping import ScrapingResult, ParsedListing
from backend.scrapers.page_fetcher import PageFetcher
from backend.scrapers.parser_factory import ParserFactory

logger = logging.getLogger(__name__)


class ScrapingService:
    def __init__(self):
        self.fetcher = PageFetcher()

    def scrape(self, url: str) -> ScrapingResult:
        """
        Coordinates fetching and parsing of a given URL.
        Returns a structured ScrapingResult without business logic.
        """
        logger.info(f"Starting scraping process for: {url}")
        try:
            if url.startswith("search://"):
                # Mock a scraping result for search queries
                parts = url.replace("search://", "").split("/")
                brand = parts[0] if len(parts) > 0 else "Unknown Brand"
                product = parts[1] if len(parts) > 1 else "Unknown Product"

                parsed_listing = ParsedListing(
                    title=f"{brand} {product}",
                    price=99.99,
                    seller_name="Global Search",
                    brand=brand,
                    marketplace="Global",
                    description=f"Search results for {product} by {brand}",
                    images_count=1
                )
                return ScrapingResult(success=True, listing=parsed_listing, raw_html="<html>Mocked Search HTML</html>")

            html = self.fetcher.fetch(url)

            parser = ParserFactory.get_parser(url)
            parsed_listing = parser.parse(html, url)

            return ScrapingResult(success=True, listing=parsed_listing, raw_html=html)
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ScrapingResult(success=False, error_message=str(e))
