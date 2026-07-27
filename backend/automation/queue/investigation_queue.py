import logging
import queue
from typing import Optional

from backend.automation.models.domain import InvestigationPlan, PlanStatus

logger = logging.getLogger(__name__)


class InvestigationQueue:
    """
    In-memory priority queue for InvestigationPlans.
    In a distributed system, this would be backed by Celery/Redis or Kafka.
    """

    def __init__(self):
        # Python's PriorityQueue sorts lowest first. We want highest priority first,
        # so we will insert items with negative priority.
        self._queue = queue.PriorityQueue()
        self._plans = {}  # Keep a dictionary for fast lookups by ID

    def enqueue(self, plan: InvestigationPlan) -> None:
        """
        Enqueues an InvestigationPlan based on its priority.
        """
        plan.status = PlanStatus.PENDING
        self._plans[plan.id] = plan
        # Negative priority because queue.PriorityQueue returns lowest numbers first
        self._queue.put((-plan.priority, plan.id))
        logger.info(f"Enqueued plan {plan.id} with priority {plan.priority}")

    def dequeue(self) -> Optional[InvestigationPlan]:
        """
        Dequeues the highest priority InvestigationPlan.
        """
        try:
            _, plan_id = self._queue.get_nowait()
            plan = self._plans.get(plan_id)
            if plan:
                plan.status = PlanStatus.IN_PROGRESS
                logger.info(f"Dequeued plan {plan_id} for execution.")
                return plan
        except queue.Empty:
            return None

    def mark_failed(self, plan_id: str, retry: bool = False) -> None:
        """
        Marks a plan as failed, and optionally re-enqueues it with lower priority.
        """
        plan = self._plans.get(plan_id)
        if not plan:
            return

        if retry and plan.priority > 0:
            logger.warning(f"Retrying failed plan {plan_id} with reduced priority.")
            plan.priority = max(0, plan.priority - 10)
            self.enqueue(plan)
        else:
            logger.error(f"Plan {plan_id} failed permanently.")
            plan.status = PlanStatus.FAILED

    def mark_completed(self, plan_id: str) -> None:
        """
        Marks a plan as completed.
        """
        plan = self._plans.get(plan_id)
        if plan:
            plan.status = PlanStatus.COMPLETED
            logger.info(f"Plan {plan_id} marked as completed.")
