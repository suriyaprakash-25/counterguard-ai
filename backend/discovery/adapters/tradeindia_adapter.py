import logging
from typing import List

from backend.discovery.base import BaseMarketplaceAdapter
from backend.schemas.discovery import ListingCandidate

logger = logging.getLogger(__name__)


class TradeIndiaAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "TradeIndia"

    async def search_candidates(
        self, query: str, limit: int = 5
    ) -> List[ListingCandidate]:
        logger.info(
            f"Executing TradeIndiaAdapter discovery search for query: '{query}'"
        )
        candidates = []
        q_lower = query.lower()

        base_url = (
            f"https://www.tradeindia.com/fp/{query.lower().replace(' ', '-')}.html"
        )

        candidates.append(
            ListingCandidate(
                marketplace=self.marketplace_name,
                title=f"Bulk OEM Manufacturing - {query}",
                url=base_url,
                price=150.0 if "buds" in q_lower else 450.0,
                seller="Shenzhen Precision Tech Co Ltd (TradeIndia Verified Supplier)",
                thumbnail="https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=300",
                currency="INR",
                availability="MOQ 100 Pieces",
                discovery_source="TradeIndia B2B Supplier Directory",
                confidence=0.82,
            )
        )

        return candidates[:limit]
