from enum import Enum
from urllib.parse import urlparse


class Marketplace(Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    EBAY = "ebay"
    ALIBABA = "alibaba"
    TRADEINDIA = "tradeindia"
    MEESHO = "meesho"
    AJIO = "ajio"
    MYNTRA = "myntra"
    UNKNOWN = "unknown"


class MarketplaceDetector:
    @staticmethod
    def detect(url: str) -> Marketplace:
        """
        Detects the marketplace from a given URL.
        """
        try:
            domain = urlparse(url).netloc.lower()

            if "amazon." in domain:
                return Marketplace.AMAZON
            elif "flipkart.com" in domain:
                return Marketplace.FLIPKART
            elif "ebay." in domain:
                return Marketplace.EBAY
            elif "alibaba.com" in domain or "aliexpress.com" in domain:
                return Marketplace.ALIBABA
            elif "tradeindia.com" in domain:
                return Marketplace.TRADEINDIA
            elif "meesho.com" in domain:
                return Marketplace.MEESHO
            elif "ajio.com" in domain:
                return Marketplace.AJIO
            elif "myntra.com" in domain:
                return Marketplace.MYNTRA
            else:
                return Marketplace.UNKNOWN
        except Exception:
            return Marketplace.UNKNOWN
