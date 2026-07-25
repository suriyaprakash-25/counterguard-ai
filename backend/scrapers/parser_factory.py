from backend.scrapers.amazon_parser import AmazonParser
from backend.scrapers.base_parser import BaseParser
from backend.scrapers.flipkart_parser import FlipkartParser
from backend.scrapers.generic_parser import GenericParser
from backend.scrapers.marketplace_detector import Marketplace, MarketplaceDetector


class ParserFactory:
    @staticmethod
    def get_parser(url: str) -> BaseParser:
        """
        Detects the marketplace and returns the appropriate parser.
        """
        marketplace = MarketplaceDetector.detect(url)

        if marketplace == Marketplace.AMAZON:
            return AmazonParser()
        elif marketplace == Marketplace.FLIPKART:
            return FlipkartParser()
        else:
            return GenericParser()
