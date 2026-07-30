import logging
from typing import List

from backend.discovery.base import BaseMarketplaceAdapter
from backend.schemas.discovery import ListingCandidate

logger = logging.getLogger(__name__)


class MeeshoAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Meesho"

    async def search_candidates(
        self, query: str, limit: int = 5
    ) -> List[ListingCandidate]:
        logger.info(f"Executing MeeshoAdapter discovery search for query: '{query}'")
        candidates = []
        q_lower = query.lower()

        base_url = f"https://www.meesho.com/search?q={query.replace(' ', '%20')}"

        candidates.append(
            ListingCandidate(
                marketplace=self.marketplace_name,
                title=f"{query} Trendy Combo Edition",
                url=f"{base_url}&s_id=MSH_901",
                price=499.0 if "buds" in q_lower or "shoes" in q_lower else 799.0,
                seller="Radha Wholesale Enterprises",
                thumbnail="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300",
                currency="INR",
                availability="In Stock",
                discovery_source="Meesho Supplier Catalog",
                confidence=0.68,
            )
        )

        if limit >= 2:
            candidates.append(
                ListingCandidate(
                    marketplace=self.marketplace_name,
                    title=f"{query} Replica Master Copy",
                    url=f"{base_url}&s_id=MSH_902",
                    price=299.0 if "buds" in q_lower or "shoes" in q_lower else 399.0,
                    seller="Fashion Hub Wholesale Surat",
                    thumbnail="https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=300",
                    currency="INR",
                    availability="In Stock",
                    discovery_source="Meesho Seller Feed",
                    confidence=0.55,
                )
            )

        return candidates[:limit]
