from backend.scrapers.ajio_parser import AjioParser
from backend.scrapers.amazon_parser import AmazonParser
from backend.scrapers.base_parser import BaseParser
from backend.scrapers.flipkart_parser import FlipkartParser
from backend.scrapers.generic_parser import GenericParser
from backend.scrapers.marketplace_detector import Marketplace, MarketplaceDetector
from backend.scrapers.meesho_parser import MeeshoParser
from backend.scrapers.myntra_parser import MyntraParser
from backend.scrapers.tradeindia_parser import TradeIndiaParser


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
        elif marketplace == Marketplace.TRADEINDIA:
            return TradeIndiaParser()
        elif marketplace == Marketplace.MEESHO:
            return MeeshoParser()
        elif marketplace == Marketplace.AJIO:
            return AjioParser()
        elif marketplace == Marketplace.MYNTRA:
            return MyntraParser()
        else:
            return GenericParser()
