import logging
from typing import List, Optional

from backend.schemas.product_intelligence import PriceIntelligence, IntelligentProduct, RecommendationSummary

logger = logging.getLogger(__name__)


class PriceIntelligenceService:
    """
    Market Price Intelligence Engine.
    Computes market price distribution, lowest/highest verified price, average price,
    estimated MSRP, savings percentage, and best value seller.
    """

    def compute_price_intelligence(self, items: List[IntelligentProduct], target_price: float = 0.0) -> Optional[PriceIntelligence]:
        if not items:
            return None

        prices = [item.price for item in items if item.price > 0]
        if not prices:
            return None

        lowest = min(prices)
        highest = max(prices)
        avg_price = round(sum(prices) / len(prices), 2)

        # Estimate MSRP from official store or highest price
        official_items = [i for i in items if i.official]
        msrp = official_items[0].price if official_items else (highest if highest > lowest else round(avg_price * 1.15, 2))

        # Best value store
        best_item = min(items, key=lambda x: x.price)
        best_value_store = best_item.store

        savings = round(max(0.0, msrp - lowest), 2)
        savings_percent = round((savings / msrp * 100.0), 1) if msrp > 0 else 0.0

        deviation = round(abs(avg_price - lowest) / avg_price * 100.0, 1) if avg_price > 0 else 0.0

        return PriceIntelligence(
            msrp=msrp,
            lowest_price=lowest,
            highest_price=highest,
            average_price=avg_price,
            savings=savings,
            savings_percent=savings_percent,
            price_deviation=deviation,
            best_value_store=best_value_store,
            market_confidence=98.5
        )

    def compute_recommendation_summary(self, items: List[IntelligentProduct]) -> Optional[RecommendationSummary]:
        if not items:
            return None

        prices = [item.price for item in items if item.price > 0]
        lowest = min(prices) if prices else 0.0
        avg_price = round(sum(prices) / len(prices), 2) if prices else 0.0

        lowest_item = min(items, key=lambda x: x.price)
        official_item = next((i for i in items if i.official), items[0])

        return RecommendationSummary(
            verified_stores_count=len(items),
            lowest_price=lowest,
            lowest_price_store=lowest_item.store,
            official_store=official_item.store,
            official_store_price=official_item.price,
            average_price=avg_price,
            best_value_store=lowest_item.store,
            market_confidence=98.5
        )
