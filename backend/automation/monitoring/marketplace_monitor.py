import logging
from typing import Any, Dict, List

from backend.automation.models.domain import MarketplaceEvent
from backend.automation.monitoring.change_detector import ChangeDetectionService

logger = logging.getLogger(__name__)


class MarketplaceMonitoringService:
    """
    Monitors marketplaces for new listings and updates to existing listings.
    Emits MarketplaceEvents when meaningful changes are detected.
    """

    def __init__(self, change_detector: ChangeDetectionService):
        self.change_detector = change_detector
        self._snapshots: Dict[
            str, Dict[str, Any]
        ] = {}  # In-memory mock for previous states

    def poll_marketplace(
        self, marketplace: str, current_listings: List[Dict[str, Any]]
    ) -> List[MarketplaceEvent]:
        """
        Polls a marketplace (simulated by passing current listings) and compares against
        previous snapshots to detect changes and generate events.
        """
        logger.info(
            f"Polling marketplace: {marketplace}. Found {len(current_listings)} listings."
        )
        events = []

        for listing in current_listings:
            listing_id = listing.get("listing_id")
            if not listing_id:
                logger.warning("Listing missing 'listing_id', skipping.")
                continue

            old_data = self._snapshots.get(listing_id)
            changes = self.change_detector.detect_changes(old_data, listing)

            for change in changes:
                event = MarketplaceEvent(
                    event_type=change["event_type"],
                    marketplace=marketplace,
                    listing_id=listing_id,
                    seller_name=listing.get("seller_name", "Unknown"),
                    data=change["data"],
                )
                events.append(event)
                logger.debug(
                    f"Generated event: {event.event_type} for listing {listing_id}"
                )

            # Update snapshot
            import copy

            self._snapshots[listing_id] = copy.deepcopy(listing)

        return events
