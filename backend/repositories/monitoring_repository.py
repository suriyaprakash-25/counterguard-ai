"""
monitoring_repository.py — Phase 2: Repository Layer for Continuous Monitoring & Watchlists
Encapsulates all database operations for SQLite persistence, eliminating in-memory data structures.
"""
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.database.engine import get_session_maker
from backend.models.monitoring import (
    MonitoringEventModel,
    MonitoringHistoryModel,
    MonitoringJobModel,
    WatchlistModel,
)

logger = logging.getLogger("counterguard.monitoring_repository")


class MonitoringJobRepository:
    def __init__(self, session: Optional[Session] = None):
        self._session_override = session

    def _get_session(self) -> Session:
        if self._session_override:
            return self._session_override
        return get_session_maker()()

    def get_all(self) -> List[MonitoringJobModel]:
        session = self._get_session()
        try:
            return (
                session.query(MonitoringJobModel)
                .order_by(MonitoringJobModel.created_at.desc())
                .all()
            )
        finally:
            if not self._session_override:
                session.close()

    def get_by_id(self, job_id: str) -> Optional[MonitoringJobModel]:
        session = self._get_session()
        try:
            return (
                session.query(MonitoringJobModel)
                .filter(MonitoringJobModel.id == job_id)
                .first()
            )
        finally:
            if not self._session_override:
                session.close()

    def save(self, job: MonitoringJobModel) -> MonitoringJobModel:
        session = self._get_session()
        try:
            job.updated_at = datetime.utcnow()
            session.merge(job)
            session.commit()
            return job
        except Exception as e:
            session.rollback()
            logger.error(
                f"[MonitoringJobRepository] Failed to save job '{job.id}': {e}"
            )
            raise
        finally:
            if not self._session_override:
                session.close()

    def set_status(self, job_id: str, status: str) -> Optional[MonitoringJobModel]:
        session = self._get_session()
        try:
            job = (
                session.query(MonitoringJobModel)
                .filter(MonitoringJobModel.id == job_id)
                .first()
            )
            if job:
                job.status = status
                job.updated_at = datetime.utcnow()
                session.commit()
            return job
        except Exception as e:
            session.rollback()
            logger.error(
                f"[MonitoringJobRepository] Failed to set status for '{job_id}': {e}"
            )
            raise
        finally:
            if not self._session_override:
                session.close()

    def delete(self, job_id: str) -> bool:
        session = self._get_session()
        try:
            job = (
                session.query(MonitoringJobModel)
                .filter(MonitoringJobModel.id == job_id)
                .first()
            )
            if job:
                session.delete(job)
                session.commit()
                return True
            return False
        finally:
            if not self._session_override:
                session.close()


class MonitoringHistoryRepository:
    def __init__(self, session: Optional[Session] = None):
        self._session_override = session

    def _get_session(self) -> Session:
        if self._session_override:
            return self._session_override
        return get_session_maker()()

    def add_record(self, record: MonitoringHistoryModel) -> MonitoringHistoryModel:
        session = self._get_session()
        try:
            session.add(record)
            session.commit()
            return record
        except Exception as e:
            session.rollback()
            logger.error(
                f"[MonitoringHistoryRepository] Failed to add execution record: {e}"
            )
            raise
        finally:
            if not self._session_override:
                session.close()

    def get_history(self, limit: int = 50) -> List[MonitoringHistoryModel]:
        session = self._get_session()
        try:
            return (
                session.query(MonitoringHistoryModel)
                .order_by(MonitoringHistoryModel.started_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            if not self._session_override:
                session.close()


class MonitoringEventRepository:
    def __init__(self, session: Optional[Session] = None):
        self._session_override = session

    def _get_session(self) -> Session:
        if self._session_override:
            return self._session_override
        return get_session_maker()()

    def add_event(self, event: MonitoringEventModel) -> MonitoringEventModel:
        session = self._get_session()
        try:
            session.add(event)
            session.commit()
            return event
        except Exception as e:
            session.rollback()
            logger.error(
                f"[MonitoringEventRepository] Failed to add monitoring event: {e}"
            )
            raise
        finally:
            if not self._session_override:
                session.close()

    def get_recent_events(self, limit: int = 20) -> List[MonitoringEventModel]:
        session = self._get_session()
        try:
            return (
                session.query(MonitoringEventModel)
                .order_by(MonitoringEventModel.timestamp.desc())
                .limit(limit)
                .all()
            )
        finally:
            if not self._session_override:
                session.close()


class WatchlistRepository:
    def __init__(self, session: Optional[Session] = None):
        self._session_override = session

    def _get_session(self) -> Session:
        if self._session_override:
            return self._session_override
        return get_session_maker()()

    def get_all(self) -> List[WatchlistModel]:
        session = self._get_session()
        try:
            return (
                session.query(WatchlistModel)
                .order_by(WatchlistModel.created_at.desc())
                .all()
            )
        finally:
            if not self._session_override:
                session.close()

    def get_enabled(self) -> List[WatchlistModel]:
        session = self._get_session()
        try:
            return (
                session.query(WatchlistModel)
                .filter(WatchlistModel.enabled == True)
                .all()
            )
        finally:
            if not self._session_override:
                session.close()

    def save(self, watchlist: WatchlistModel) -> WatchlistModel:
        session = self._get_session()
        try:
            watchlist.updated_at = datetime.utcnow()
            session.merge(watchlist)
            session.commit()
            return watchlist
        except Exception as e:
            session.rollback()
            logger.error(
                f"[WatchlistRepository] Failed to save watchlist '{watchlist.id}': {e}"
            )
            raise
        finally:
            if not self._session_override:
                session.close()

    def delete(self, watchlist_id: str) -> bool:
        session = self._get_session()
        try:
            item = (
                session.query(WatchlistModel)
                .filter(WatchlistModel.id == watchlist_id)
                .first()
            )
            if item:
                session.delete(item)
                session.commit()
                return True
            return False
        finally:
            if not self._session_override:
                session.close()


# Singleton repository instances
monitoring_job_repo = MonitoringJobRepository()
monitoring_history_repo = MonitoringHistoryRepository()
monitoring_event_repo = MonitoringEventRepository()
watchlist_repo = WatchlistRepository()
