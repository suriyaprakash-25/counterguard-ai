import logging

import requests
from requests.exceptions import RequestException

from backend.exceptions import (
    InvalidListingError,
    ScrapingConnectionError,
    ScrapingTimeoutError,
)
from backend.settings import settings

logger = logging.getLogger(__name__)


class PageFetcher:
    def __init__(self, timeout: int = settings.SCRAPE_TIMEOUT):
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def fetch(self, url: str) -> str:
        """
        Fetches the HTML content of a given URL.
        Raises an exception if the request fails or times out.
        """
        url = (url or "").strip()
        logger.info(f"Fetching URL: {url}")
        try:
            response = requests.get(
                url, headers=self.headers, timeout=self.timeout, allow_redirects=True
            )
            response.raise_for_status()
            logger.info(f"Successfully fetched {url} (Status: {response.status_code})")
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in (403, 503):
                try:
                    import cloudscraper

                    logger.info(
                        f"HTTP {e.response.status_code} anti-bot challenge for {url}. Engaging cloudscraper bypass..."
                    )
                    scraper = cloudscraper.create_scraper(
                        browser={
                            "browser": "chrome",
                            "platform": "windows",
                            "desktop": True,
                        }
                    )
                    cs_resp = scraper.get(url, timeout=self.timeout)
                    if cs_resp.status_code == 200:
                        logger.info(
                            f"Cloudscraper successfully bypassed anti-bot for {url} (Status 200)"
                        )
                        return cs_resp.text
                except Exception as cs_err:
                    logger.warning(f"Cloudscraper bypass failed: {cs_err}")

            logger.error(f"HTTP Error fetching {url}: {e}")
            if e.response is not None and e.response.status_code == 404:
                raise InvalidListingError(f"Listing not found (404): {url}")
            raise ScrapingConnectionError(f"HTTP Error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching {url}: {e}")
            raise ScrapingTimeoutError(f"Timeout: {e}")
        except RequestException as e:
            logger.error(f"Connection error fetching {url}: {e}")
            raise ScrapingConnectionError(f"Connection error: {e}")
