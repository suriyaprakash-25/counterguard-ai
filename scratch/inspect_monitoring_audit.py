"""
inspect_monitoring_audit.py — Empirical Reality Verification Script for Continuous Monitoring
"""
import sqlite3

from backend.repositories.monitoring_repository import (
    monitoring_history_repo,
    monitoring_job_repo,
)
from backend.services.monitoring_orchestrator import monitoring_orchestrator
from backend.services.monitoring_scheduler import monitoring_scheduler


def run_audit():
    print("=== 1. SQLITE TABLE ROW COUNTS ===")
    conn = sqlite3.connect("./counterguard.db")
    cursor = conn.cursor()

    tables = [
        "monitoring_jobs",
        "monitoring_history",
        "monitoring_events",
        "watchlists",
    ]
    counts = {}
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = cursor.fetchone()[0]
        except Exception as e:
            counts[t] = f"Error: {e}"
        print(f"Table '{t}': {counts[t]} rows")

    print("\n=== 2. PERSISTED MONITORING JOBS ===")
    jobs = monitoring_job_repo.get_all()
    for j in jobs:
        print(
            f"ID: {j.id} | Name: {j.name} | Interval: {j.interval} | Status: {j.status} | Scans: {j.total_scans} | Disc: {j.total_discovered} | Inv: {j.total_investigations} | Last: {j.last_run}"
        )

    print("\n=== 3. APSCHEDULER RUNNING JOBS ===")
    monitoring_scheduler.start()
    aps_jobs = monitoring_scheduler._scheduler.get_jobs()
    print(f"APScheduler Active Jobs Count: {len(aps_jobs)}")
    for aj in aps_jobs:
        print(f"Job ID: {aj.id} | Next Run: {aj.next_run_time} | Trigger: {aj.trigger}")

    print("\n=== 4. LATEST 5 MONITORING EXECUTION HISTORY RECORDS ===")
    history = monitoring_history_repo.get_history(limit=5)
    for h in history:
        print(
            f"Exec ID: {h.id} | Job: {h.job_id} | Status: {h.status} | Duration: {h.duration_ms}ms | Disc: {h.discoveries} | Inv: {h.investigations} | Time: {h.started_at}"
        )

    print("\n=== 5. DASHBOARD METRICS COMPUTATION ===")
    status_resp = monitoring_orchestrator.get_monitoring_status()
    print(f"Active Jobs: {status_resp.active_jobs}")
    print(f"Completed Scans: {status_resp.completed_scans}")
    print(f"Total Discovered Listings: {status_resp.total_discovered_listings}")
    print(f"Total Auto Investigations: {status_resp.total_auto_investigations}")

    conn.close()


if __name__ == "__main__":
    run_audit()
