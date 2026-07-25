import logging

from backend.schemas.scraping import ScrapingResult
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
            html = self.fetcher.fetch(url)

            parser = ParserFactory.get_parser(url)
            parsed_listing = parser.parse(html, url)

            return ScrapingResult(success=True, listing=parsed_listing, raw_html=html)
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ScrapingResult(success=False, error_message=str(e))
