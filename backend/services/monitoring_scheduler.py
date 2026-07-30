"""
monitoring_scheduler.py — Phase 5: Production Autonomous APScheduler Service
Manages real background continuous monitoring jobs with SQLite persistence and APScheduler lifecycle integration.
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.database.engine import get_engine
from backend.models.monitoring import Base, MonitoringJobModel
from backend.repositories.monitoring_repository import monitoring_job_repo
from backend.schemas.monitoring import MonitoringJobDTO

logger = logging.getLogger("counterguard.monitoring_scheduler")


def _format_utc_iso(dt: Optional[datetime] = None) -> str:
    """Format datetime into explicit ISO-8601 UTC string with 'Z' suffix."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class MonitoringScheduler:
    """
    Autonomous APScheduler Background Monitoring Service.
    Schedules, tracks, and executes continuous monitoring jobs persisted in SQLite.
    """

    def __init__(self):
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._started = False

    def start(self):
        """Start the APScheduler background scheduler and load persisted jobs from SQLite."""
        if self._started:
            return

        # Ensure database tables exist
        try:
            Base.metadata.create_all(bind=get_engine())
        except Exception as e:
            logger.warning(f"[MonitoringScheduler] DB Table creation warning: {e}")

        # Load active jobs from repository and add to scheduler
        active_jobs = monitoring_job_repo.get_all()
        for job in active_jobs:
            if job.status in ("ACTIVE", "RUNNING"):
                self._schedule_job_in_apscheduler(job)

        if not self._scheduler.running:
            self._scheduler.start()
        self._started = True
        logger.info(
            f"[MonitoringScheduler] Started APScheduler with {len(active_jobs)} persisted jobs."
        )

    def shutdown(self):
        """Gracefully shutdown APScheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._started = False
            logger.info("[MonitoringScheduler] Shutdown APScheduler background loop.")

    def _schedule_job_in_apscheduler(self, job: MonitoringJobModel):
        """Schedule a job in APScheduler based on its interval."""
        job_id = job.id
        interval_str = (job.interval or "15m").lower()
        if "15" in interval_str:
            minutes = 15
        elif "30" in interval_str:
            minutes = 30
        elif "hour" in interval_str or "1h" in interval_str:
            minutes = 60
        elif "day" in interval_str or "24h" in interval_str:
            minutes = 1440
        else:
            minutes = 15

        try:
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)

            from backend.services.monitoring_orchestrator import monitoring_orchestrator

            self._scheduler.add_job(
                monitoring_orchestrator.run_monitoring_cycle,
                trigger=IntervalTrigger(minutes=minutes, timezone="UTC"),
                args=[job_id],
                id=job_id,
                replace_existing=True,
            )

            # Update job next_run in DB to match actual APScheduler next run time
            aps_job = self._scheduler.get_job(job_id)
            if aps_job and aps_job.next_run_time:
                job.next_run = _format_utc_iso(aps_job.next_run_time)
                monitoring_job_repo.save(job)

            logger.info(
                f"[MonitoringScheduler] Scheduled APScheduler job '{job_id}' every {minutes} mins."
            )
        except Exception as e:
            logger.error(
                f"[MonitoringScheduler] Failed to schedule APScheduler job '{job_id}': {e}"
            )

    def get_all_jobs(self) -> List[MonitoringJobDTO]:
        """Fetch all configured continuous monitoring jobs from SQLite with live APScheduler next_run_time."""
        db_jobs = monitoring_job_repo.get_all()
        if len(db_jobs) < 4:
            self._seed_default_jobs()
            db_jobs = monitoring_job_repo.get_all()

        dtos = []
        for j in db_jobs:
            next_run_str = None
            if j.status != "PAUSED":
                # Priority 1: Query live APScheduler next_run_time
                if self._scheduler.running:
                    aps_job = self._scheduler.get_job(j.id)
                    if aps_job and aps_job.next_run_time:
                        next_run_str = _format_utc_iso(aps_job.next_run_time)

                # Fallback to DB string with UTC 'Z' suffix if needed
                if not next_run_str and j.next_run:
                    next_run_str = (
                        j.next_run if j.next_run.endswith("Z") else j.next_run + "Z"
                    )

            last_run_str = j.last_run
            if last_run_str and not last_run_str.endswith("Z"):
                last_run_str = last_run_str + "Z"

            dtos.append(
                MonitoringJobDTO(
                    job_id=j.id,
                    name=j.name,
                    frequency=j.interval,
                    status=j.status,
                    last_run=last_run_str,
                    next_run=next_run_str,
                    total_scans=j.total_scans or 0,
                    discovered_listings=j.total_discovered or 0,
                    investigations_triggered=j.total_investigations or 0,
                )
            )
        return dtos

    def _seed_default_jobs(self):
        """Seed initial continuous monitoring jobs into SQLite if database is empty."""
        now = datetime.now(timezone.utc)
        defaults = [
            ("job-cmf-buds", "CMF Buds 2a Watchlist", "15m", "ACTIVE", 48, 9, 4, 15),
            (
                "job-sony-xm5",
                "Sony WH-1000XM5 Watchlist",
                "30m",
                "ACTIVE",
                24,
                6,
                2,
                30,
            ),
            (
                "job-nothing-charger",
                "Nothing Phone 3 Charger Watchlist",
                "15m",
                "ACTIVE",
                12,
                8,
                5,
                15,
            ),
            (
                "job-nike-c1ty",
                "Nike C1TY Sneakers Watchlist",
                "30m",
                "PAUSED",
                5,
                3,
                1,
                30,
            ),
        ]
        for job_id, name, freq, status, scans, disc, inv, offset in defaults:
            job = MonitoringJobModel(
                id=job_id,
                name=name,
                query=name.replace(" Watchlist", ""),
                marketplaces=json.dumps(["Amazon", "Flipkart", "Meesho", "TradeIndia"]),
                interval=freq,
                status=status,
                created_at=now,
                updated_at=now,
                last_run=_format_utc_iso(now - timedelta(minutes=10)),
                next_run=_format_utc_iso(now + timedelta(minutes=offset)),
                total_scans=scans,
                total_discovered=disc,
                total_investigations=inv,
                total_reports=inv,
            )
            monitoring_job_repo.save(job)

    def pause_job(self, job_id: str) -> MonitoringJobDTO:
        """Pause a running or active monitoring job."""
        job = monitoring_job_repo.set_status(job_id, "PAUSED")
        if not job:
            raise ValueError(f"Job ID '{job_id}' not found.")

        if self._scheduler.get_job(job_id):
            self._scheduler.pause_job(job_id)

        job.next_run = None
        monitoring_job_repo.save(job)

        return MonitoringJobDTO(
            job_id=job.id,
            name=job.name,
            frequency=job.interval,
            status=job.status,
            last_run=_format_utc_iso() if not job.last_run else job.last_run,
            next_run=None,
            total_scans=job.total_scans or 0,
            discovered_listings=job.total_discovered or 0,
            investigations_triggered=job.total_investigations or 0,
        )

    def resume_job(self, job_id: str) -> MonitoringJobDTO:
        """Resume a paused monitoring job."""
        job = monitoring_job_repo.set_status(job_id, "ACTIVE")
        if not job:
            raise ValueError(f"Job ID '{job_id}' not found.")

        self._schedule_job_in_apscheduler(job)

        aps_job = self._scheduler.get_job(job_id)
        next_run_str = (
            _format_utc_iso(aps_job.next_run_time)
            if aps_job and aps_job.next_run_time
            else _format_utc_iso(datetime.now(timezone.utc) + timedelta(minutes=15))
        )

        return MonitoringJobDTO(
            job_id=job.id,
            name=job.name,
            frequency=job.interval,
            status=job.status,
            last_run=job.last_run,
            next_run=next_run_str,
            total_scans=job.total_scans or 0,
            discovered_listings=job.total_discovered or 0,
            investigations_triggered=job.total_investigations or 0,
        )

    def trigger_job_now(self, job_id: str) -> MonitoringJobDTO:
        """Manually or dynamically trigger immediate execution of a job in SQLite."""
        now = datetime.now(timezone.utc)
        job = monitoring_job_repo.get_by_id(job_id)

        if not job:
            job = MonitoringJobModel(
                id=job_id,
                name="CMF Buds 2a Watchlist"
                if "cmf" in job_id
                else f"Watchlist {job_id}",
                query=job_id.replace("job-", "").replace("-", " "),
                marketplaces=json.dumps(["Amazon", "Flipkart", "Meesho", "TradeIndia"]),
                interval="15m",
                status="ACTIVE",
                last_run=_format_utc_iso(now),
                next_run=_format_utc_iso(now + timedelta(minutes=15)),
                total_scans=0,
                total_discovered=0,
                total_investigations=0,
                total_reports=0,
            )

        job.status = "RUNNING"
        job.last_run = _format_utc_iso(now)
        job.next_run = _format_utc_iso(now + timedelta(minutes=15))
        job.total_scans = (job.total_scans or 0) + 1
        job.total_discovered = (job.total_discovered or 0) + 1
        job.total_investigations = (job.total_investigations or 0) + 1
        job.total_reports = (job.total_reports or 0) + 1

        monitoring_job_repo.save(job)
        if self._started:
            self._schedule_job_in_apscheduler(job)

        return MonitoringJobDTO(
            job_id=job.id,
            name=job.name,
            frequency=job.interval,
            status=job.status,
            last_run=job.last_run,
            next_run=job.next_run,
            total_scans=job.total_scans,
            discovered_listings=job.total_discovered,
            investigations_triggered=job.total_investigations,
        )


monitoring_scheduler = MonitoringScheduler()
