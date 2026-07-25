from enum import Enum
from urllib.parse import urlparse


class Marketplace(Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    EBAY = "ebay"
    ALIBABA = "alibaba"
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
            else:
                return Marketplace.UNKNOWN
        except Exception:
            return Marketplace.UNKNOWN
