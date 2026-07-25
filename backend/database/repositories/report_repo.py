import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.repositories.interfaces import IReportRepository
from backend.exceptions import CounterGuardError
from backend.models.report import ReportModel

logger = logging.getLogger(__name__)


class ReportRepository(IReportRepository):
    """
    SQLAlchemy implementation of IReportRepository.
    Supports SQLite and PostgreSQL transparently.
    """

    def __init__(self, session: Session):
        self._session = session

    def add(self, report: ReportModel) -> ReportModel:
        try:
            self._session.add(report)
            self._session.commit()
            self._session.refresh(report)
            return report
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(f"Failed to add report {report.id}: {e}")
            raise CounterGuardError(f"Database error adding report: {e}") from e

    def get_by_id(self, report_id: str) -> Optional[ReportModel]:
        try:
            return self._session.get(ReportModel, report_id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve report {report_id}: {e}")
            raise CounterGuardError(f"Database error querying report: {e}") from e

    def get_by_investigation(self, investigation_id: str) -> Optional[ReportModel]:
        try:
            return (
                self._session.query(ReportModel)
                .filter(ReportModel.investigation_id == investigation_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to retrieve report for investigation {investigation_id}: {e}"
            )
            raise CounterGuardError(
                f"Database error querying investigation report: {e}"
            ) from e

    def delete(self, report_id: str) -> bool:
        try:
            report = self.get_by_id(report_id)
            if not report:
                return False
            self._session.delete(report)
            self._session.commit()
            return True
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(f"Failed to delete report {report_id}: {e}")
            raise CounterGuardError(f"Database error deleting report: {e}") from e
