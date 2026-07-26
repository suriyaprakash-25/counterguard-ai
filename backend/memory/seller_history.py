import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SellerHistoryRecord(BaseModel):
    """Represents a discrete historical memory record for a seller entity."""

    id: str
    seller_id: str
    seller_name: str
    marketplace: Optional[str] = None
    trust_score: float = 50.0
    infringement_count: int = 0
    verified_merchant: bool = False
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SellerHistoryRepository(ABC):
    """Abstract repository interface for managing seller historical memory."""

    @abstractmethod
    def save(self, record: SellerHistoryRecord) -> None:
        """Persist or update a seller history record."""
        pass

    @abstractmethod
    def get_by_id(self, record_id: str) -> Optional[SellerHistoryRecord]:
        """Retrieve a record by its unique ID."""
        pass

    @abstractmethod
    def get_by_seller_id(
        self, seller_id: str, marketplace: Optional[str] = None
    ) -> List[SellerHistoryRecord]:
        """Retrieve all memory records associated with a given target seller ID."""
        pass

    @abstractmethod
    def delete(self, record_id: str) -> None:
        """Delete a seller history record by ID."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 50) -> List[SellerHistoryRecord]:
        """List recent seller history records up to limit."""
        pass


class SQLiteSellerHistoryRepository(SellerHistoryRepository):
    """SQLite implementation of SellerHistoryRepository using structured JSON blob storage."""

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
                CREATE TABLE IF NOT EXISTS seller_history_memory (
                    id TEXT PRIMARY KEY,
                    seller_id TEXT NOT NULL,
                    seller_name TEXT NOT NULL,
                    marketplace TEXT,
                    trust_score REAL,
                    last_seen TEXT,
                    data JSON NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_seller_history_seller_id ON seller_history_memory(seller_id, marketplace)"
            )

    def save(self, record: SellerHistoryRecord) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO seller_history_memory (
                    id, seller_id, seller_name, marketplace, trust_score, last_seen, data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.seller_id,
                    record.seller_name,
                    record.marketplace,
                    record.trust_score,
                    record.last_seen.isoformat(),
                    record.model_dump_json(),
                ),
            )

    def get_by_id(self, record_id: str) -> Optional[SellerHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM seller_history_memory WHERE id = ?", (record_id,)
        )
        row = cursor.fetchone()
        if row:
            return SellerHistoryRecord.model_validate_json(row[0])
        return None

    def get_by_seller_id(
        self, seller_id: str, marketplace: Optional[str] = None
    ) -> List[SellerHistoryRecord]:
        conn = self._get_connection()
        if marketplace:
            cursor = conn.execute(
                "SELECT data FROM seller_history_memory WHERE seller_id = ? AND marketplace = ? ORDER BY last_seen DESC",
                (seller_id, marketplace),
            )
        else:
            cursor = conn.execute(
                "SELECT data FROM seller_history_memory WHERE seller_id = ? ORDER BY last_seen DESC",
                (seller_id,),
            )
        return [
            SellerHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def delete(self, record_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM seller_history_memory WHERE id = ?", (record_id,))

    def list_all(self, limit: int = 50) -> List[SellerHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM seller_history_memory ORDER BY last_seen DESC LIMIT ?",
            (limit,),
        )
        return [
            SellerHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def close(self) -> None:
        if not self._external_conn:
            self._conn.close()
