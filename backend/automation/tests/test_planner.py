from backend.automation.models.domain import EventType, MarketplaceEvent
from backend.automation.planner.planner_service import PlannerService


def test_planner_service_new_listing():
    planner = PlannerService()
    event = MarketplaceEvent(
        event_type=EventType.NEW_LISTING,
        marketplace="Test",
        listing_id="1",
        seller_name="Test",
    )

    plan = planner.plan_investigation(event)
    assert plan.priority == 50
    assert len(plan.tasks) == 4
    agent_names = [t.agent_name for t in plan.tasks]
    assert "PriceAgent" in agent_names
    assert "SellerAgent" in agent_names


def test_planner_service_price_change():
    planner = PlannerService()
    event = MarketplaceEvent(
        event_type=EventType.PRICE_CHANGE,
        marketplace="Test",
        listing_id="1",
        seller_name="Test",
    )

    plan = planner.plan_investigation(event)
    assert plan.priority == 40
    assert len(plan.tasks) == 1
    assert plan.tasks[0].agent_name == "PriceAgent"


def test_planner_service_watchlist():
    planner = PlannerService()
    event = MarketplaceEvent(
        event_type=EventType.WATCHLIST_TRIGGER,
        marketplace="Test",
        listing_id="1",
        seller_name="Test",
    )

    plan = planner.plan_investigation(event)
    assert plan.priority == 100
    assert len(plan.tasks) == 4
