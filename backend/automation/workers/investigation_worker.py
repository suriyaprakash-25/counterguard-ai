import logging
import threading
import time

from backend.automation.queue.investigation_queue import InvestigationQueue
from backend.orchestrator.builder import build_graph
from backend.schemas.investigation import InvestigationRequest

logger = logging.getLogger(__name__)


class InvestigationWorker:
    """
    Pops InvestigationPlans from the queue and executes them via LangGraph.
    """

    def __init__(self, queue: InvestigationQueue):
        self.queue = queue
        self._running = False
        self._thread = None
        # Build the graph once for this worker
        self.graph = build_graph()

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="InvestigationWorker"
        )
        self._thread.start()
        logger.info("InvestigationWorker started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("InvestigationWorker stopped.")

    def _loop(self):
        while self._running:
            plan = self.queue.dequeue()
            if not plan:
                time.sleep(1)
                continue

            logger.info(
                f"Worker picked up InvestigationPlan {plan.id} for event {plan.event_id}"
            )
            try:
                # We mock a request based on the plan's event data. In a real system,
                # the event holds the exact URL or listing data.
                request = InvestigationRequest(
                    listing_url=f"http://example.com/listing/{plan.event_id}",
                    priority=plan.priority,
                )

                state = {"request": request, "investigation_plan": plan}

                # Run the graph synchronously
                self.graph.invoke(state)

                self.queue.mark_completed(plan.id)
                logger.info(
                    f"Worker successfully completed InvestigationPlan {plan.id}"
                )

            except Exception as e:
                logger.error(f"Worker failed InvestigationPlan {plan.id}: {e}")
                self.queue.mark_failed(plan.id, retry=True)
