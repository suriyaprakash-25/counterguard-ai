import logging
import urllib.parse
from typing import Optional, Set, Tuple

from backend.schemas.discovery_engine import SourceCandidate

logger = logging.getLogger(__name__)


class SourceVerificationEngine:
    """
    SourceVerificationEngine (Sprint 17 Phase 2 Deliverable)

    Performs deterministic, rule-based verification checks on candidate sources.
    Uses ZERO LLM calls to ensure fast, deterministic, non-flaky verification.
    """

    ALLOWED_BRAND_DOMAINS: Set[str] = {
        "nothing.tech",
        "nike.com",
        "apple.com",
        "samsung.com",
        "sony.com",
        "adidas.com",
        "gucci.com",
        "ray-ban.com",
        "rolex.com",
        "bose.com",
        "dell.com",
        "lenovo.com",
        "microsoft.com",
        "amazon.com",
        "bestbuy.com",
        "walmart.com",
        "flipkart.com",
    }

    def verify_https(self, url: str) -> bool:
        """
        Verifies that the candidate URL uses secure HTTPS protocol.
        """
        if not url:
            return False
        try:
            parsed = urllib.parse.urlparse(url.strip())
            return parsed.scheme.lower() == "https"
        except Exception:
            return False

    def verify_domain(
        self, url: str, allowed_domains: Optional[Set[str]] = None
    ) -> bool:
        """
        Verifies whether the candidate URL domain belongs to a whitelisted/allowed domain set.
        """
        if not url:
            return False
        target_set = allowed_domains or self.ALLOWED_BRAND_DOMAINS
        try:
            parsed = urllib.parse.urlparse(url.strip().lower())
            host = parsed.hostname.replace("www.", "") if parsed.hostname else ""
            for allowed in target_set:
                if host == allowed or host.endswith("." + allowed):
                    return True
            return False
        except Exception:
            return False

    def verify_brand(self, title_or_url: str, brand: str) -> bool:
        """
        Verifies whether the title or URL string contains the expected brand name hint.
        """
        if not brand or not brand.strip():
            return True
        clean_text = title_or_url.strip().lower()
        clean_brand = brand.strip().lower()
        return clean_brand in clean_text

    def verify_product_match(self, title: str, query: str) -> bool:
        """
        Verifies basic product query token match in candidate title.
        """
        if not query or not query.strip():
            return True
        tokens = [t.lower() for t in query.strip().split() if len(t) > 2]
        if not tokens:
            return True
        clean_title = title.lower()
        matched = [t for t in tokens if t in clean_title]
        # Requires at least one matching query token
        return len(matched) > 0

    def verify_source(
        self, candidate: SourceCandidate, brand: str = ""
    ) -> Tuple[bool, str]:
        """
        Primary verification entry point: Runs all deterministic checks on a candidate source.
        Returns Tuple[is_verified: bool, reasoning: str].
        """
        if not candidate or not candidate.url:
            return False, "Rejected: Missing candidate URL"

        if not self.verify_https(candidate.url):
            return False, f"Rejected: Non-HTTPS protocol URL '{candidate.url}'"

        if not self.verify_domain(candidate.url):
            return (
                False,
                f"Rejected: Domain not in allowed brand registry for URL '{candidate.url}'",
            )

        if brand and not self.verify_brand(f"{candidate.title} {candidate.url}", brand):
            return (
                False,
                f"Rejected: Brand hint '{brand}' mismatch in candidate title/URL",
            )

        return (
            True,
            f"Verified: Passed HTTPS, domain whitelist, and brand matching for provider '{candidate.provider}'",
        )
