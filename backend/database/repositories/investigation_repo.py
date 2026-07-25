import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.repositories.interfaces import IInvestigationRepository
from backend.exceptions import CounterGuardError
from backend.models.investigation import InvestigationModel

logger = logging.getLogger(__name__)


class InvestigationRepository(IInvestigationRepository):
    """
    SQLAlchemy implementation of IInvestigationRepository.
    Supports SQLite and PostgreSQL transparently.
    """

    def __init__(self, session: Session):
        self._session = session

    def add(self, investigation: InvestigationModel) -> InvestigationModel:
        try:
            self._session.add(investigation)
            self._session.commit()
            self._session.refresh(investigation)
            return investigation
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(f"Failed to save investigation {investigation.id}: {e}")
            raise CounterGuardError(f"Database error adding investigation: {e}") from e

    def get_by_id(self, investigation_id: str) -> Optional[InvestigationModel]:
        try:
            return self._session.get(InvestigationModel, investigation_id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve investigation {investigation_id}: {e}")
            raise CounterGuardError(
                f"Database error querying investigation: {e}"
            ) from e

    def get_all(self, limit: int = 100, offset: int = 0) -> List[InvestigationModel]:
        try:
            query = (
                self._session.query(InvestigationModel)
                .order_by(InvestigationModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve investigation list: {e}")
            raise CounterGuardError(
                f"Database error listing investigations: {e}"
            ) from e

    def update_status(
        self, investigation_id: str, status: str
    ) -> Optional[InvestigationModel]:
        try:
            investigation = self.get_by_id(investigation_id)
            if not investigation:
                return None
            investigation.status = status
            self._session.commit()
            self._session.refresh(investigation)
            return investigation
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(
                f"Failed to update status for investigation {investigation_id}: {e}"
            )
            raise CounterGuardError(
                f"Database error updating investigation status: {e}"
            ) from e

    def delete(self, investigation_id: str) -> bool:
        try:
            investigation = self.get_by_id(investigation_id)
            if not investigation:
                return False
            self._session.delete(investigation)
            self._session.commit()
            return True
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(f"Failed to delete investigation {investigation_id}: {e}")
            raise CounterGuardError(
                f"Database error deleting investigation: {e}"
            ) from e
