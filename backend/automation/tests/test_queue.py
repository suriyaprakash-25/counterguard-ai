from backend.automation.models.domain import InvestigationPlan, PlanStatus
from backend.automation.queue.investigation_queue import InvestigationQueue


def test_investigation_queue_priority():
    queue = InvestigationQueue()

    plan1 = InvestigationPlan(event_id="1", priority=10)
    plan2 = InvestigationPlan(event_id="2", priority=50)
    plan3 = InvestigationPlan(event_id="3", priority=20)

    queue.enqueue(plan1)
    queue.enqueue(plan2)
    queue.enqueue(plan3)

    # Highest priority should be dequeued first
    dequeued1 = queue.dequeue()
    assert dequeued1.id == plan2.id

    dequeued2 = queue.dequeue()
    assert dequeued2.id == plan3.id

    dequeued3 = queue.dequeue()
    assert dequeued3.id == plan1.id


def test_investigation_queue_retry():
    queue = InvestigationQueue()
    plan = InvestigationPlan(event_id="1", priority=50)
    queue.enqueue(plan)

    popped = queue.dequeue()
    assert popped.status == PlanStatus.IN_PROGRESS

    queue.mark_failed(popped.id, retry=True)

    # Priority should be reduced
    assert plan.priority == 40

    popped_again = queue.dequeue()
    assert popped_again.id == plan.id
