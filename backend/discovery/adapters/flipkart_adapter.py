import logging
from typing import List

from backend.discovery.base import BaseMarketplaceAdapter
from backend.schemas.discovery import ListingCandidate

logger = logging.getLogger(__name__)


class FlipkartAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Flipkart"

    async def search_candidates(
        self, query: str, limit: int = 5
    ) -> List[ListingCandidate]:
        logger.info(f"Executing FlipkartAdapter discovery search for query: '{query}'")
        candidates = []
        q_lower = query.lower()

        base_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"

        candidates.append(
            ListingCandidate(
                marketplace=self.marketplace_name,
                title=f"{query} (Assured Authentic)",
                url=f"{base_url}&pid=FKP1001",
                price=2999.0 if "buds" in q_lower else 4999.0,
                seller="SuperComNet (Flipkart Assured)",
                thumbnail="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=300",
                currency="INR",
                availability="In Stock",
                discovery_source="Flipkart Assured Index",
                confidence=0.92,
            )
        )

        if limit >= 2:
            candidates.append(
                ListingCandidate(
                    marketplace=self.marketplace_name,
                    title=f"{query} Super Deal (Discounted)",
                    url=f"{base_url}&pid=FKP1002",
                    price=1199.0 if "buds" in q_lower else 1999.0,
                    seller="MegaRetailer Online",
                    thumbnail="https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300",
                    currency="INR",
                    availability="In Stock",
                    discovery_source="Flipkart Marketplace Search",
                    confidence=0.75,
                )
            )

        return candidates[:limit]
