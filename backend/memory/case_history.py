import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CaseHistoryRecord(BaseModel):
    """Represents a finalized or ongoing investigation case record in long-term memory."""

    case_id: str
    listing_id: str
    listing_title: Optional[str] = None
    seller_id: Optional[str] = None
    brand_name: Optional[str] = None
    verdict: str = "PENDING"
    risk_score: float = 0.0
    action_taken: str = "NONE"
    investigation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    evidence_hashes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CaseHistoryRepository(ABC):
    """Abstract repository interface for storing and retrieving past investigation cases."""

    @abstractmethod
    def save(self, record: CaseHistoryRecord) -> None:
        """Persist or update an investigation case history record."""
        pass

    @abstractmethod
    def get_by_case_id(self, case_id: str) -> Optional[CaseHistoryRecord]:
        """Retrieve a case record by its unique case_id."""
        pass

    @abstractmethod
    def get_by_listing_id(self, listing_id: str) -> List[CaseHistoryRecord]:
        """Retrieve all historical cases executed against a specific target listing_id."""
        pass

    @abstractmethod
    def get_by_seller_id(self, seller_id: str) -> List[CaseHistoryRecord]:
        """Retrieve historical investigation cases associated with a target seller ID."""
        pass

    @abstractmethod
    def delete(self, case_id: str) -> None:
        """Delete a case history record by case_id."""
        pass

    @abstractmethod
    def list_recent(self, limit: int = 50) -> List[CaseHistoryRecord]:
        """List recent case history records up to limit, ordered by timestamp descending."""
        pass


class SQLiteCaseHistoryRepository(CaseHistoryRepository):
    """SQLite implementation of CaseHistoryRepository."""

    def __init__(
        self,
        db_path: str = ":memory:",
        connection: Optional[sqlite3.Connection] = None,
    ):
        self.db_path = db_path
        self._external_conn = connection is not None
        if connection is not None:
            self._conn = connection
        else:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return self._conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS case_history_memory (
                    case_id TEXT PRIMARY KEY,
                    listing_id TEXT NOT NULL,
                    seller_id TEXT,
                    brand_name TEXT,
                    verdict TEXT,
                    risk_score REAL,
                    timestamp TEXT,
                    data JSON NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_case_history_listing ON case_history_memory(listing_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_case_history_seller ON case_history_memory(seller_id)"
            )

    def save(self, record: CaseHistoryRecord) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO case_history_memory (
                    case_id, listing_id, seller_id, brand_name, verdict, risk_score, timestamp, data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.case_id,
                    record.listing_id,
                    record.seller_id,
                    record.brand_name.lower().strip() if record.brand_name else None,
                    record.verdict,
                    record.risk_score,
                    record.investigation_timestamp.isoformat(),
                    record.model_dump_json(),
                ),
            )

    def get_by_case_id(self, case_id: str) -> Optional[CaseHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM case_history_memory WHERE case_id = ?", (case_id,)
        )
        row = cursor.fetchone()
        if row:
            return CaseHistoryRecord.model_validate_json(row[0])
        return None

    def get_by_listing_id(self, listing_id: str) -> List[CaseHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM case_history_memory WHERE listing_id = ? ORDER BY timestamp DESC",
            (listing_id,),
        )
        return [
            CaseHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def get_by_seller_id(self, seller_id: str) -> List[CaseHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM case_history_memory WHERE seller_id = ? ORDER BY timestamp DESC",
            (seller_id,),
        )
        return [
            CaseHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def delete(self, case_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM case_history_memory WHERE case_id = ?", (case_id,)
            )

    def list_recent(self, limit: int = 50) -> List[CaseHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM case_history_memory ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        return [
            CaseHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def close(self) -> None:
        if not self._external_conn:
            self._conn.close()
