from backend.automation.models.domain import (
    EventType,
    MarketplaceEvent,
    WatchlistEntityType,
    WatchlistItem,
)
from backend.automation.monitoring.change_detector import ChangeDetectionService
from backend.automation.monitoring.marketplace_monitor import (
    MarketplaceMonitoringService,
)
from backend.automation.watchlists.watchlist_service import WatchlistService


def test_change_detector():
    detector = ChangeDetectionService()

    # Test new listing
    new_data = {"price": 100, "seller_name": "TestSeller", "image_urls": ["url1"]}
    changes = detector.detect_changes(None, new_data)
    assert len(changes) == 1
    assert changes[0]["event_type"] == EventType.NEW_LISTING

    # Test price drop
    old_data = {"price": 100, "seller_name": "TestSeller", "image_urls": ["url1"]}
    new_data = {"price": 80, "seller_name": "TestSeller", "image_urls": ["url1"]}
    changes = detector.detect_changes(old_data, new_data)
    assert len(changes) == 1
    assert changes[0]["event_type"] == EventType.PRICE_CHANGE

    # Test multiple changes
    new_data_2 = {"price": 100, "seller_name": "NewSeller", "image_urls": ["url2"]}
    changes_2 = detector.detect_changes(old_data, new_data_2)
    assert len(changes_2) == 2
    event_types = [c["event_type"] for c in changes_2]
    assert EventType.SELLER_CHANGE in event_types
    assert EventType.IMAGE_CHANGE in event_types


def test_marketplace_monitor():
    detector = ChangeDetectionService()
    monitor = MarketplaceMonitoringService(detector)

    listings = [{"listing_id": "1", "price": 100, "seller_name": "Seller1"}]
    events = monitor.poll_marketplace("TestMarket", listings)
    assert len(events) == 1
    assert events[0].event_type == EventType.NEW_LISTING

    # Poll again with a price drop
    listings[0]["price"] = 50
    events_2 = monitor.poll_marketplace("TestMarket", listings)
    assert len(events_2) == 1
    assert events_2[0].event_type == EventType.PRICE_CHANGE


def test_watchlist_service():
    service = WatchlistService()
    service.add_to_watchlist(
        WatchlistItem(
            entity_type=WatchlistEntityType.SELLER,
            entity_value="BadActor",
            watch_reason="Fraud",
        )
    )

    event = MarketplaceEvent(
        event_type=EventType.PRICE_CHANGE,
        marketplace="Test",
        listing_id="1",
        seller_name="BadActor",
    )
    modified_event = service.check_event(event)

    assert modified_event.event_type == EventType.WATCHLIST_TRIGGER
    assert modified_event.data["watch_reason"] == "Fraud"
