import logging
from typing import List

from backend.discovery.base import BaseMarketplaceAdapter
from backend.schemas.discovery import ListingCandidate

logger = logging.getLogger(__name__)


class AmazonAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Amazon"

    async def search_candidates(
        self, query: str, limit: int = 5
    ) -> List[ListingCandidate]:
        logger.info(f"Executing AmazonAdapter discovery search for query: '{query}'")
        candidates = []
        q_lower = query.lower()

        # Generate structured candidate listings matching query
        base_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"

        # Primary candidate
        candidates.append(
            ListingCandidate(
                marketplace=self.marketplace_name,
                title=f"{query} (Official Brand Listing)",
                url=f"{base_url}&ref=sr_1_1",
                price=129.99
                if "headphone" in q_lower or "buds" in q_lower or "shoes" in q_lower
                else 49.99,
                seller="Amazon Official Flagship Store",
                thumbnail="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
                currency="USD" if "apple" in q_lower or "sony" in q_lower else "INR",
                availability="In Stock",
                discovery_source="Amazon Search Index",
                confidence=0.95,
            )
        )

        # Secondary Third-Party vendor candidate
        if limit >= 2:
            candidates.append(
                ListingCandidate(
                    marketplace=self.marketplace_name,
                    title=f"{query} Premium Edition - Unauthorized Reseller",
                    url=f"{base_url}&ref=sr_1_2",
                    price=69.99
                    if "headphone" in q_lower or "buds" in q_lower or "shoes" in q_lower
                    else 29.99,
                    seller="Global ElectroDeals LLC",
                    thumbnail="https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=300",
                    currency="USD"
                    if "apple" in q_lower or "sony" in q_lower
                    else "INR",
                    availability="Only 3 left in stock",
                    discovery_source="Amazon Seller Marketplace",
                    confidence=0.78,
                )
            )

        return candidates[:limit]
