import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.repositories.interfaces import IEvidenceRepository
from backend.exceptions import CounterGuardError
from backend.models.evidence import EvidenceModel

logger = logging.getLogger(__name__)


class EvidenceRepository(IEvidenceRepository):
    """
    SQLAlchemy implementation of IEvidenceRepository.
    Supports SQLite and PostgreSQL transparently.
    """

    def __init__(self, session: Session):
        self._session = session

    def add(self, evidence: EvidenceModel) -> EvidenceModel:
        try:
            self._session.add(evidence)
            self._session.commit()
            self._session.refresh(evidence)
            return evidence
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(f"Failed to add evidence {evidence.id}: {e}")
            raise CounterGuardError(f"Database error adding evidence: {e}") from e

    def add_batch(self, evidence_list: List[EvidenceModel]) -> List[EvidenceModel]:
        try:
            self._session.add_all(evidence_list)
            self._session.commit()
            for ev in evidence_list:
                self._session.refresh(ev)
            return evidence_list
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(
                f"Failed to add batch of {len(evidence_list)} evidence items: {e}"
            )
            raise CounterGuardError(f"Database error adding evidence batch: {e}") from e

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceModel]:
        try:
            return self._session.get(EvidenceModel, evidence_id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve evidence {evidence_id}: {e}")
            raise CounterGuardError(f"Database error querying evidence: {e}") from e

    def get_by_investigation(self, investigation_id: str) -> List[EvidenceModel]:
        try:
            query = (
                self._session.query(EvidenceModel)
                .filter(EvidenceModel.investigation_id == investigation_id)
                .order_by(EvidenceModel.timestamp.asc(), EvidenceModel.id.asc())
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to retrieve evidence for investigation {investigation_id}: {e}"
            )
            raise CounterGuardError(
                f"Database error querying investigation evidence: {e}"
            ) from e

    def delete_by_investigation(self, investigation_id: str) -> int:
        try:
            count = (
                self._session.query(EvidenceModel)
                .filter(EvidenceModel.investigation_id == investigation_id)
                .delete(synchronize_session=False)
            )
            self._session.commit()
            return count
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error(
                f"Failed to delete evidence for investigation {investigation_id}: {e}"
            )
            raise CounterGuardError(
                f"Database error deleting investigation evidence: {e}"
            ) from e
