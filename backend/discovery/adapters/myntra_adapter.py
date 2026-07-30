import logging
from typing import List

from backend.discovery.base import BaseMarketplaceAdapter
from backend.schemas.discovery import ListingCandidate

logger = logging.getLogger(__name__)


class MyntraAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Myntra"

    async def search_candidates(
        self, query: str, limit: int = 5
    ) -> List[ListingCandidate]:
        logger.info(f"Executing MyntraAdapter discovery search for query: '{query}'")
        candidates = []
        q_lower = query.lower()

        base_url = f"https://www.myntra.com/{query.lower().replace(' ', '-')}"

        candidates.append(
            ListingCandidate(
                marketplace=self.marketplace_name,
                title=f"{query} Original Edition",
                url=f"{base_url}/buy",
                price=2799.0 if "buds" in q_lower else 4499.0,
                seller="Flashstar Commerce (Myntra Verified Partner)",
                thumbnail="https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=300",
                currency="INR",
                availability="In Stock",
                discovery_source="Myntra Official Catalog",
                confidence=0.93,
            )
        )

        return candidates[:limit]
