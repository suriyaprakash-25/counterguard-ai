import logging
from typing import List

from backend.automation.models.domain import (
    EventType,
    MarketplaceEvent,
    WatchlistEntityType,
    WatchlistItem,
)

logger = logging.getLogger(__name__)


class WatchlistService:
    """
    Maintains a list of watched entities (sellers, brands, products, keywords).
    Intercepts marketplace events and escalates them if they match a watched entity.
    """

    def __init__(self):
        self._watchlist: List[WatchlistItem] = []

    def add_to_watchlist(self, item: WatchlistItem) -> None:
        """
        Adds an entity to the watchlist.
        """
        self._watchlist.append(item)
        logger.info(f"Added {item.entity_type} '{item.entity_value}' to watchlist.")

    def check_event(self, event: MarketplaceEvent) -> MarketplaceEvent:
        """
        Checks if an incoming event matches anything on the watchlist.
        If it does, escalates the event type to WATCHLIST_TRIGGER.
        Returns the (potentially modified) event.
        """
        for item in self._watchlist:
            if (
                item.entity_type == WatchlistEntityType.SELLER
                and item.entity_value.lower() == event.seller_name.lower()
            ):
                logger.warning(
                    f"Watchlist trigger: Seller {event.seller_name} matched watchlist item {item.id}."
                )
                event.event_type = EventType.WATCHLIST_TRIGGER
                event.data["watch_reason"] = item.watch_reason
                return event

            # Additional logic for brands/keywords would go here, examining event.data
            brand = event.data.get("new_listing", {}).get("brand", "").lower()
            if (
                brand
                and item.entity_type == WatchlistEntityType.BRAND
                and item.entity_value.lower() == brand
            ):
                logger.warning(
                    f"Watchlist trigger: Brand {brand} matched watchlist item {item.id}."
                )
                event.event_type = EventType.WATCHLIST_TRIGGER
                event.data["watch_reason"] = item.watch_reason
                return event

        return event
