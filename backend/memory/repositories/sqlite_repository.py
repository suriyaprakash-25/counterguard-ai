import sqlite3
from typing import List, Optional

from backend.memory.models.domain import InvestigationEpisode, SellerProfile
from backend.memory.repositories.interfaces import (
    InvestigationRepository,
    SellerRepository,
)


class SQLiteInvestigationRepository(InvestigationRepository):
    """SQLite implementation of InvestigationRepository."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        # For :memory:, we must keep the connection open to persist data
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _get_connection(self):
        return self._conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    seller_name TEXT,
                    marketplace TEXT,
                    timestamp TEXT,
                    verdict TEXT,
                    risk_score REAL,
                    summary TEXT,
                    data JSON
                )
            """
            )

    def save(self, episode: InvestigationEpisode) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO episodes (id, seller_name, marketplace, timestamp, verdict, risk_score, summary, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    episode.id,
                    episode.seller_identity.name,
                    episode.marketplace,
                    episode.investigation_timestamp.isoformat(),
                    episode.verdict,
                    episode.risk_score,
                    episode.summary,
                    episode.model_dump_json(),
                ),
            )

    def get_by_id(self, episode_id: str) -> Optional[InvestigationEpisode]:
        cursor = self._get_connection().execute(
            "SELECT data FROM episodes WHERE id = ?", (episode_id,)
        )
        row = cursor.fetchone()
        if row:
            return InvestigationEpisode.model_validate_json(row[0])
        return None

    def delete(self, episode_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))

    def list_recent(self, limit: int = 10) -> List[InvestigationEpisode]:
        cursor = self._get_connection().execute(
            "SELECT data FROM episodes ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        return [
            InvestigationEpisode.model_validate_json(row[0])
            for row in cursor.fetchall()
        ]


class SQLiteSellerRepository(SellerRepository):
    """SQLite implementation of SellerRepository."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _get_connection(self):
        return self._conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sellers (
                    name TEXT PRIMARY KEY,
                    domain TEXT,
                    data JSON
                )
            """
            )

    def save(self, profile: SellerProfile) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO sellers (name, domain, data)
                VALUES (?, ?, ?)
            """,
                (
                    profile.identity.name,
                    profile.identity.domain,
                    profile.model_dump_json(),
                ),
            )

    def get_by_identity(
        self, name: str, domain: Optional[str] = None
    ) -> Optional[SellerProfile]:
        cursor = self._get_connection().execute(
            "SELECT data FROM sellers WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        if row:
            return SellerProfile.model_validate_json(row[0])
        return None

    def search(self, query: str) -> List[SellerProfile]:
        cursor = self._get_connection().execute(
            "SELECT data FROM sellers WHERE name LIKE ?", (f"%{query}%",)
        )
        return [SellerProfile.model_validate_json(row[0]) for row in cursor.fetchall()]
