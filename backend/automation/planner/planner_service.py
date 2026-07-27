import logging
from typing import List

from backend.automation.models.domain import (
    EventType,
    InvestigationPlan,
    InvestigationTask,
    MarketplaceEvent,
)

logger = logging.getLogger(__name__)


class PlannerService:
    """
    Evaluates events to plan investigations. Selects required specialist agents,
    estimates priority, and calculates cost and runtime.
    """

    def plan_investigation(self, event: MarketplaceEvent) -> InvestigationPlan:
        """
        Generates an InvestigationPlan based on the incoming MarketplaceEvent.
        """
        logger.info(f"Planning investigation for event {event.id} ({event.event_type})")

        tasks = self.select_agents(event)
        priority = self.estimate_priority(event)
        cost = self.estimate_cost(tasks)
        runtime = self.estimate_runtime(tasks)

        plan = InvestigationPlan(
            event_id=event.id,
            priority=priority,
            estimated_cost=cost,
            estimated_runtime_seconds=runtime,
            tasks=tasks,
        )
        return plan

    def select_agents(self, event: MarketplaceEvent) -> List[InvestigationTask]:
        """
        Selects which specialist agents are required based on the event type.
        """
        tasks = []
        if event.event_type in [EventType.NEW_LISTING, EventType.WATCHLIST_TRIGGER]:
            # Full investigation
            tasks.append(InvestigationTask(agent_name="PriceAgent", priority=1))
            tasks.append(InvestigationTask(agent_name="SellerAgent", priority=1))
            tasks.append(InvestigationTask(agent_name="BrandAgent", priority=1))
            tasks.append(InvestigationTask(agent_name="ReviewAgent", priority=1))
        elif event.event_type == EventType.PRICE_CHANGE:
            tasks.append(InvestigationTask(agent_name="PriceAgent", priority=2))
        elif event.event_type == EventType.SELLER_CHANGE:
            tasks.append(InvestigationTask(agent_name="SellerAgent", priority=1))
        elif (
            event.event_type == EventType.IMAGE_CHANGE
            or event.event_type == EventType.DESCRIPTION_CHANGE
        ):
            tasks.append(InvestigationTask(agent_name="BrandAgent", priority=2))
        elif event.event_type == EventType.REVIEW_CHANGE:
            tasks.append(InvestigationTask(agent_name="ReviewAgent", priority=3))

        return tasks

    def estimate_priority(self, event: MarketplaceEvent) -> int:
        """
        Estimates the priority of the investigation (higher is more critical).
        """
        if event.event_type == EventType.WATCHLIST_TRIGGER:
            return 100
        elif event.event_type == EventType.SELLER_CHANGE:
            return 80
        elif event.event_type == EventType.NEW_LISTING:
            return 50
        elif event.event_type == EventType.PRICE_CHANGE:
            return 40
        return 20

    def estimate_cost(self, tasks: List[InvestigationTask]) -> float:
        """
        Estimates the LLM cost of the planned investigation.
        """
        # Roughly $0.01 per agent
        return len(tasks) * 0.01

    def estimate_runtime(self, tasks: List[InvestigationTask]) -> int:
        """
        Estimates runtime in seconds.
        """
        # Roughly 5 seconds per agent
        return len(tasks) * 5
