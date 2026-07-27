import time

from backend.automation.scheduler.scheduler_service import SchedulerService


def test_scheduler_service():
    scheduler = SchedulerService()

    execution_count = 0

    def dummy_task():
        nonlocal execution_count
        execution_count += 1

    scheduler.add_job("test_job", dummy_task, interval_seconds=1)

    scheduler.start()
    time.sleep(1.5)
    scheduler.stop()

    # Depending on exact timing, should have run at least once or twice
    assert execution_count >= 1
