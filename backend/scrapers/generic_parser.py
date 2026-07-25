import logging
import re
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from backend.schemas.scraping import ParsedListing
from backend.scrapers.base_parser import BaseParser
from backend.scrapers.marketplace_detector import Marketplace, MarketplaceDetector

logger = logging.getLogger(__name__)


class GenericParser(BaseParser):
    def parse(self, html: str, url: str) -> ParsedListing:
        """
        Extracts structured data from HTML content.
        Uses heuristic patterns to support multiple marketplaces.
        """
        soup = BeautifulSoup(html, "lxml")

        # Detection logic is handled by Factory, but fallback available
        detector = MarketplaceDetector()
        detected = detector.detect(url)
        marketplace = (
            detected.value
            if detected != Marketplace.UNKNOWN
            else self._extract_marketplace(url)
        )
        title = self._extract_title(soup)
        price = self._extract_price(soup)
        seller_name = self._extract_seller(soup)
        seller_rating = self._extract_seller_rating(soup)
        brand = self._extract_brand(soup)
        images_count = self._extract_images_count(soup)
        description = self._extract_description(soup)
        availability = self._extract_availability(soup)
        warranty = self._extract_warranty(soup)

        currency = self._extract_currency(soup)
        shipping = self._extract_shipping(soup)
        category = self._extract_category(soup)

        return ParsedListing(
            title=title,
            price=price,
            seller_name=seller_name,
            seller_rating=seller_rating,
            brand=brand,
            images_count=images_count,
            description=description,
            availability=availability,
            warranty_info=warranty,
            marketplace=marketplace,
            currency=currency,
            shipping=shipping,
            category=category,
        )

    def _extract_marketplace(self, url: str) -> str:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        title_tag = soup.find("h1")
        if title_tag:
            return title_tag.get_text(strip=True)
        if soup.title:
            return soup.title.get_text(strip=True)
        return None

    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        text_content = soup.get_text()
        price_match = re.search(r"[\$€£]\s*(\d+[\.,]\d{2})", text_content)
        if price_match:
            try:
                val = price_match.group(1).replace(",", ".")
                if val.count(".") > 1:
                    parts = val.split(".")
                    val = "".join(parts[:-1]) + "." + parts[-1]
                return float(val)
            except ValueError:
                pass
        return None

    def _extract_currency(self, soup: BeautifulSoup) -> Optional[str]:
        text_content = soup.get_text()
        if "$" in text_content or "USD" in text_content:
            return "USD"
        if "€" in text_content or "EUR" in text_content:
            return "EUR"
        if "£" in text_content or "GBP" in text_content:
            return "GBP"
        return None

    def _extract_shipping(self, soup: BeautifulSoup) -> Optional[str]:
        shipping_text = soup.find(
            string=re.compile(r"shipping|delivery", re.IGNORECASE)
        )
        if shipping_text and shipping_text.parent:
            text = shipping_text.parent.get_text(strip=True)
            if len(text) < 100:
                return text
        return None

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        category_text = soup.find(
            string=re.compile(r"category|department", re.IGNORECASE)
        )
        if category_text and category_text.parent:
            nxt = category_text.parent.find_next_sibling()
            if nxt:
                return nxt.get_text(strip=True)
        return None

    def _extract_seller(self, soup: BeautifulSoup) -> Optional[str]:
        seller_elements = soup.find_all(
            string=re.compile(r"sold by|seller", re.IGNORECASE)
        )
        for el in seller_elements:
            parent = el.parent
            if parent and parent.name in ["div", "span", "a"]:
                text = parent.get_text(strip=True)
                if len(text) < 50:
                    text = re.sub(r"(?i)\bsold by\b|\bseller\b:?\s*", "", text).strip()
                    return text
        return "Unknown Seller"

    def _extract_seller_rating(self, soup: BeautifulSoup) -> Optional[float]:
        text = soup.get_text()
        rating_match = re.search(r"(\d[\.,]\d)\s*out of\s*5", text, re.IGNORECASE)
        if rating_match:
            try:
                return float(rating_match.group(1).replace(",", "."))
            except ValueError:
                pass
        return None

    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        brand_el = soup.find(string=re.compile(r"brand", re.IGNORECASE))
        if brand_el:
            parent = brand_el.parent
            if parent:
                text = parent.get_text(strip=True)
                text = re.sub(r"(?i)\bbrand\b:?\s*", "", text).strip()
                if text:
                    return text
                nxt = parent.find_next_sibling()
                if nxt:
                    return nxt.get_text(strip=True)
        return None

    def _extract_images_count(self, soup: BeautifulSoup) -> int:
        imgs = soup.find_all("img")
        count = 0
        for img in imgs:
            try:
                w = int(img.get("width", 100))
                h = int(img.get("height", 100))
                if w >= 50 or h >= 50:
                    count += 1
            except ValueError:
                count += 1
        return count

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        desc_div = soup.find(
            lambda tag: tag.name == "div"
            and any(
                "description" in c.lower()
                for c in tag.get("class", []) + [tag.get("id", "")]
            )
        )
        if desc_div:
            return desc_div.get_text(separator=" ", strip=True)
        return None

    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        stock_text = soup.find(
            string=re.compile(r"in stock|out of stock", re.IGNORECASE)
        )
        if stock_text:
            return stock_text.strip()
        return None

    def _extract_warranty(self, soup: BeautifulSoup) -> Optional[str]:
        warranty = soup.find(string=re.compile(r"warranty", re.IGNORECASE))
        if warranty and warranty.parent:
            text = warranty.parent.get_text(strip=True)
            if len(text) < 100:
                return text
        return None
