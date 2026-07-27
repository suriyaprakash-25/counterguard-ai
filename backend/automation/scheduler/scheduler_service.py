import logging
import threading
import time
from typing import Callable, Dict

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Lightweight, thread-based scheduler for triggering periodic background tasks.
    Designed to be easily swapped with APScheduler or Celery Beat in production.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict] = {}
        self._running = False
        self._thread = None

    def add_job(self, job_id: str, func: Callable, interval_seconds: int) -> None:
        """
        Registers a function to be executed periodically.
        """
        self._jobs[job_id] = {"func": func, "interval": interval_seconds, "last_run": 0}
        logger.info(f"Registered job {job_id} to run every {interval_seconds} seconds.")

    def start(self) -> None:
        """
        Starts the background scheduler loop.
        """
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="SchedulerThread"
        )
        self._thread.start()
        logger.info("Scheduler started.")

    def stop(self) -> None:
        """
        Stops the scheduler.
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("Scheduler stopped.")

    def _loop(self) -> None:
        """
        The main polling loop.
        """
        while self._running:
            current_time = time.time()
            for job_id, job_info in self._jobs.items():
                if current_time - job_info["last_run"] >= job_info["interval"]:
                    logger.debug(f"Executing scheduled job: {job_id}")
                    try:
                        job_info["func"]()
                    except Exception as e:
                        logger.error(f"Scheduled job {job_id} failed: {e}")
                    finally:
                        job_info["last_run"] = time.time()

            # Sleep briefly to prevent high CPU usage
            time.sleep(1)
