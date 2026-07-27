from typing import Any, Dict, List, Optional

from backend.automation.models.domain import EventType


class ChangeDetectionService:
    """
    Detects meaningful changes between historical and current listing snapshots.
    Generates appropriate EventTypes.
    """

    def detect_changes(
        self, old_data: Optional[Dict[str, Any]], new_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compares old and new data to identify specific changes.
        Returns a list of dicts describing the change events.
        """
        changes = []

        if not old_data:
            # It's a completely new listing
            changes.append(
                {"event_type": EventType.NEW_LISTING, "data": {"new_listing": new_data}}
            )
            return changes

        # Price change detection
        old_price = old_data.get("price")
        new_price = new_data.get("price")
        if old_price is not None and new_price is not None and old_price != new_price:
            # Calculate significant drop or hike (e.g. 10% diff)
            if abs(old_price - new_price) / old_price > 0.05:
                changes.append(
                    {
                        "event_type": EventType.PRICE_CHANGE,
                        "data": {"old_price": old_price, "new_price": new_price},
                    }
                )

        # Seller change detection
        old_seller = old_data.get("seller_name")
        new_seller = new_data.get("seller_name")
        if old_seller != new_seller:
            changes.append(
                {
                    "event_type": EventType.SELLER_CHANGE,
                    "data": {"old_seller": old_seller, "new_seller": new_seller},
                }
            )

        # Image/Description change detection
        if old_data.get("image_urls") != new_data.get("image_urls"):
            changes.append(
                {
                    "event_type": EventType.IMAGE_CHANGE,
                    "data": {
                        "old_images": old_data.get("image_urls"),
                        "new_images": new_data.get("image_urls"),
                    },
                }
            )

        if old_data.get("description") != new_data.get("description"):
            changes.append(
                {"event_type": EventType.DESCRIPTION_CHANGE, "data": {"changed": True}}
            )

        # Inventory change detection
        old_inv = old_data.get("inventory_count")
        new_inv = new_data.get("inventory_count")
        if old_inv != new_inv:
            changes.append(
                {
                    "event_type": EventType.INVENTORY_CHANGE,
                    "data": {"old_inventory": old_inv, "new_inventory": new_inv},
                }
            )

        return changes
