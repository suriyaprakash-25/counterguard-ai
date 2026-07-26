from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MarketplaceAPIWrapperInterface(ABC):
    """Abstract contract for Marketplace API service wrappers."""

    @abstractmethod
    def get_listing_details(
        self, listing_id: str, marketplace: str = "amazon"
    ) -> Dict[str, Any]:
        """Retrieve detailed product metadata for a target e-commerce listing."""
        pass

    @abstractmethod
    def get_seller_reputation(
        self, seller_id: str, marketplace: str = "amazon"
    ) -> Dict[str, Any]:
        """Retrieve seller trustworthiness metrics and verified status."""
        pass

    @abstractmethod
    def verify_pricing(
        self, listing_id: str, current_price: float, marketplace: str = "amazon"
    ) -> Dict[str, Any]:
        """Compare current listing price against historical norms and detect anomalies."""
        pass


class GoogleSearchWrapperInterface(ABC):
    """Abstract contract for Google Search / OSINT service wrappers."""

    @abstractmethod
    def search_web(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """Execute general web search query for open-source intelligence."""
        pass

    @abstractmethod
    def search_images(
        self, image_url: str, similarity_threshold: float = 0.80
    ) -> Dict[str, Any]:
        """Perform reverse image search to detect replica photos or unauthorized stock images."""
        pass


class BrandRegistryWrapperInterface(ABC):
    """Abstract contract for Brand & Trademark Registry service wrappers."""

    @abstractmethod
    def lookup_trademark(self, brand_name: str) -> Dict[str, Any]:
        """Verify trademark status, owner entity, and registration ID."""
        pass

    @abstractmethod
    def verify_reseller(self, brand_name: str, seller_name: str) -> Dict[str, Any]:
        """Check whether a target seller is an authorized distributor or reseller for a brand."""
        pass

    @abstractmethod
    def check_catalog(self, brand_name: str, product_title: str) -> Dict[str, Any]:
        """Verify if a product specification matches official manufacturer catalog records."""
        pass


class ExchangeRateWrapperInterface(ABC):
    """Abstract contract for Exchange Rate currency conversion service wrappers."""

    @abstractmethod
    def get_rate(
        self, target_currency: str, base_currency: Optional[str] = None
    ) -> float:
        """Retrieve foreign exchange conversion rate between base and target currency."""
        pass

    @abstractmethod
    def convert(
        self, amount: float, target_currency: str, base_currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert a numerical price amount from base currency into target currency."""
        pass


class WhoisWrapperInterface(ABC):
    """Abstract contract for WHOIS domain intelligence service wrappers."""

    @abstractmethod
    def lookup_domain(self, domain: str) -> Dict[str, Any]:
        """Query WHOIS records to determine domain age, registration privacy, and registrar info."""
        pass

    @abstractmethod
    def get_registrar_info(self, domain: str) -> Dict[str, Any]:
        """Get summarized registrar contact and sponsorship records for a domain."""
        pass
