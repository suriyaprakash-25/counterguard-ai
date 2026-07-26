import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BrandHistoryRecord(BaseModel):
    """Represents historical intelligence and tracking data for a monitored brand."""

    id: str
    brand_name: str
    trademark_reg_number: Optional[str] = None
    authorized_distributors: List[str] = Field(default_factory=list)
    known_infringer_seller_ids: List[str] = Field(default_factory=list)
    total_cases_investigated: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BrandHistoryRepository(ABC):
    """Abstract repository interface for managing brand memory and known threats."""

    @abstractmethod
    def save(self, record: BrandHistoryRecord) -> None:
        """Persist or update a brand historical memory record."""
        pass

    @abstractmethod
    def get_by_id(self, record_id: str) -> Optional[BrandHistoryRecord]:
        """Retrieve a brand history record by its unique ID."""
        pass

    @abstractmethod
    def get_by_brand_name(self, brand_name: str) -> List[BrandHistoryRecord]:
        """Retrieve all memory records associated with a target brand name."""
        pass

    @abstractmethod
    def delete(self, record_id: str) -> None:
        """Delete a brand history record by ID."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 50) -> List[BrandHistoryRecord]:
        """List recently updated brand history records up to limit."""
        pass


class SQLiteBrandHistoryRepository(BrandHistoryRepository):
    """SQLite implementation of BrandHistoryRepository."""

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
                CREATE TABLE IF NOT EXISTS brand_history_memory (
                    id TEXT PRIMARY KEY,
                    brand_name TEXT NOT NULL,
                    trademark_reg_number TEXT,
                    last_updated TEXT,
                    data JSON NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_brand_history_name ON brand_history_memory(brand_name)"
            )

    def save(self, record: BrandHistoryRecord) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO brand_history_memory (
                    id, brand_name, trademark_reg_number, last_updated, data
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.brand_name.lower().strip(),
                    record.trademark_reg_number,
                    record.last_updated.isoformat(),
                    record.model_dump_json(),
                ),
            )

    def get_by_id(self, record_id: str) -> Optional[BrandHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM brand_history_memory WHERE id = ?", (record_id,)
        )
        row = cursor.fetchone()
        if row:
            return BrandHistoryRecord.model_validate_json(row[0])
        return None

    def get_by_brand_name(self, brand_name: str) -> List[BrandHistoryRecord]:
        clean_name = brand_name.lower().strip()
        cursor = self._get_connection().execute(
            "SELECT data FROM brand_history_memory WHERE brand_name = ? ORDER BY last_updated DESC",
            (clean_name,),
        )
        return [
            BrandHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def delete(self, record_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM brand_history_memory WHERE id = ?", (record_id,))

    def list_all(self, limit: int = 50) -> List[BrandHistoryRecord]:
        cursor = self._get_connection().execute(
            "SELECT data FROM brand_history_memory ORDER BY last_updated DESC LIMIT ?",
            (limit,),
        )
        return [
            BrandHistoryRecord.model_validate_json(row[0]) for row in cursor.fetchall()
        ]

    def close(self) -> None:
        if not self._external_conn:
            self._conn.close()
