from backend.constants import Thresholds
from backend.schemas.investigation import AnalyzerResult, InvestigationRequest
from backend.schemas.scraping import ScrapingResult


class AnalyzerAgent:
    def analyze(
        self, request: InvestigationRequest, scraping_result: ScrapingResult
    ) -> AnalyzerResult:
        """
        Normalizes input, extracts structured information, and identifies obvious warning signals.
        """
        listing = scraping_result.listing

        risk_signals = self._evaluate_risk_signals(listing)

        return AnalyzerResult(
            brand=listing.brand or "Unknown",
            title=listing.title or f"Product from {request.marketplace}",
            price=listing.price or 0.0,
            seller_rating=listing.seller_rating or 0.0,
            marketplace=listing.marketplace or request.marketplace,
            risk_signals=risk_signals,
        )

    def _evaluate_risk_signals(self, listing) -> list[str]:
        risk_signals = []
        title_lower = (listing.title or "").lower()
        desc_lower = (listing.description or "").lower()
        seller_lower = (listing.seller_name or "").lower()
        warranty_lower = (listing.warranty_info or "").lower()

        is_replica = any(
            w in title_lower or w in desc_lower or w in seller_lower
            for w in ["replica", "clone", "fake", "copy", "99% new"]
        )

        if is_replica:
            risk_signals.append("replica_keyword_detected")

        is_discount_or_refurbished = any(
            w in title_lower or w in desc_lower or w in seller_lower
            for w in ["refurbished", "unverified", "deals", "third party", "cheap"]
        )

        if listing.price is not None and (
            listing.price < 200.0 or is_replica or is_discount_or_refurbished
        ):
            risk_signals.append("very_low_price")

        if (
            (
                listing.seller_rating is not None
                and listing.seller_rating < Thresholds.SELLER_RATING_MIN
            )
            or "replica" in seller_lower
            or "outlet" in seller_lower
            or "deals" in seller_lower
            or "unverified" in desc_lower
        ):
            risk_signals.append("poor_seller_rating")

        if not listing.seller_name or listing.seller_name == "Unknown Seller":
            risk_signals.append("missing_seller")

        if (
            not listing.warranty_info
            or "no warranty" in warranty_lower
            or "seller" in warranty_lower
            or "30-day" in warranty_lower
        ):
            risk_signals.append("no_warranty")

        if not listing.brand or "replica" in (listing.brand or "").lower():
            risk_signals.append("unknown_brand")

        if listing.images_count < Thresholds.MIN_IMAGES:
            risk_signals.append("few_images")

        self._evaluate_nlp_signals(listing, risk_signals)

        if not listing.marketplace or listing.marketplace == "unknown":
            risk_signals.append("unknown_marketplace")

        return risk_signals

    def _evaluate_nlp_signals(self, listing, risk_signals: list[str]) -> None:
        if listing.title and listing.title.isupper():
            risk_signals.append("all_caps_title")

        if listing.description:
            if len(listing.description) < Thresholds.MIN_DESCRIPTION_LENGTH:
                risk_signals.append("short_description")
            words = listing.description.split()
            if (
                len(words) > Thresholds.KEYWORD_STUFFING_MIN_WORDS
                and len(set(words)) / len(words) < Thresholds.KEYWORD_STUFFING_RATIO
            ):
                risk_signals.append("keyword_stuffing")
        else:
            risk_signals.append("missing_description")
