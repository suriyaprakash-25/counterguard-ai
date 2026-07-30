import asyncio
import logging
from typing import Dict, List, Optional

from backend.discovery.adapters import (
    AjioAdapter,
    AmazonAdapter,
    FlipkartAdapter,
    MeeshoAdapter,
    MyntraAdapter,
    TradeIndiaAdapter,
)
from backend.discovery.base import BaseMarketplaceAdapter
from backend.schemas.discovery import ListingCandidate

logger = logging.getLogger(__name__)


class MarketplaceRouter:
    """
    Marketplace Router subsystem.
    Manages adapter registration and executes parallel searches across configured marketplaces.
    """

    def __init__(self):
        self._adapters: Dict[str, BaseMarketplaceAdapter] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        adapters = [
            AmazonAdapter(),
            FlipkartAdapter(),
            MeeshoAdapter(),
            TradeIndiaAdapter(),
            AjioAdapter(),
            MyntraAdapter(),
        ]
        for adapter in adapters:
            self.register_adapter(adapter)

    def register_adapter(self, adapter: BaseMarketplaceAdapter) -> None:
        self._adapters[adapter.marketplace_name.lower()] = adapter
        logger.info(f"Registered Marketplace Adapter: '{adapter.marketplace_name}'")

    def get_supported_marketplaces(self) -> List[str]:
        return [adapter.marketplace_name for adapter in self._adapters.values()]

    async def search(
        self,
        query: str,
        target_marketplaces: Optional[List[str]] = None,
        limit_per_marketplace: int = 5,
    ) -> List[ListingCandidate]:
        """
        Executes parallel candidate search across selected or all registered marketplace adapters.
        """
        selected_adapters: List[BaseMarketplaceAdapter] = []

        if target_marketplaces:
            target_lowers = {m.lower() for m in target_marketplaces}
            for name_lower, adapter in self._adapters.items():
                if name_lower in target_lowers:
                    selected_adapters.append(adapter)
        else:
            selected_adapters = list(self._adapters.values())

        if not selected_adapters:
            logger.warning("No matching marketplace adapters found for search query.")
            return []

        # Execute parallel async discovery calls
        tasks = [
            adapter.search_candidates(query=query, limit=limit_per_marketplace)
            for adapter in selected_adapters
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        candidates: List[ListingCandidate] = []
        for idx, res in enumerate(results):
            adapter_name = selected_adapters[idx].marketplace_name
            if isinstance(res, Exception):
                logger.error(
                    f"Marketplace Adapter '{adapter_name}' search failed: {res}"
                )
            elif isinstance(res, list):
                candidates.extend(res)

        # Sort candidates by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates
