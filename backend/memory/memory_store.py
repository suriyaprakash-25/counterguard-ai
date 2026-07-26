import logging
import sqlite3
from abc import ABC, abstractmethod
from typing import Optional

from backend.memory.brand_history import (
    BrandHistoryRecord,
    BrandHistoryRepository,
    SQLiteBrandHistoryRepository,
)
from backend.memory.case_history import (
    CaseHistoryRecord,
    CaseHistoryRepository,
    SQLiteCaseHistoryRepository,
)
from backend.memory.seller_history import (
    SellerHistoryRecord,
    SellerHistoryRepository,
    SQLiteSellerHistoryRepository,
)

logger = logging.getLogger(__name__)


class MemoryStoreInterface(ABC):
    """
    Abstract contract for a unified Long-Term Memory store.
    Provides repository abstractions for Seller, Brand, and Case history
    without depending on LangGraph or any AI reasoning layers.
    """

    @property
    @abstractmethod
    def seller_history(self) -> SellerHistoryRepository:
        """Access the seller history repository abstraction."""
        pass

    @property
    @abstractmethod
    def brand_history(self) -> BrandHistoryRepository:
        """Access the brand history repository abstraction."""
        pass

    @property
    @abstractmethod
    def case_history(self) -> CaseHistoryRepository:
        """Access the case history repository abstraction."""
        pass

    @abstractmethod
    def record_investigation(
        self,
        case_record: CaseHistoryRecord,
        seller_record: Optional[SellerHistoryRecord] = None,
        brand_record: Optional[BrandHistoryRecord] = None,
    ) -> None:
        """Persist investigation results across all relevant history repositories in a single operation."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Clear all stored history records from the underlying memory repositories."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connections or release resources held by the memory store."""
        pass


class MemoryStore(MemoryStoreInterface):
    """
    Concrete implementation of MemoryStoreInterface supporting SQLite and repository dependency injection.
    Completely independent of LangGraph and AI agents.
    """

    def __init__(
        self,
        db_path: str = ":memory:",
        seller_repo: Optional[SellerHistoryRepository] = None,
        brand_repo: Optional[BrandHistoryRepository] = None,
        case_repo: Optional[CaseHistoryRepository] = None,
    ):
        self.db_path = db_path
        self._managed_connection: Optional[sqlite3.Connection] = None

        if seller_repo and brand_repo and case_repo:
            self._seller_repo = seller_repo
            self._brand_repo = brand_repo
            self._case_repo = case_repo
        else:
            self._managed_connection = sqlite3.connect(
                self.db_path, check_same_thread=False
            )
            self._seller_repo = seller_repo or SQLiteSellerHistoryRepository(
                db_path=self.db_path, connection=self._managed_connection
            )
            self._brand_repo = brand_repo or SQLiteBrandHistoryRepository(
                db_path=self.db_path, connection=self._managed_connection
            )
            self._case_repo = case_repo or SQLiteCaseHistoryRepository(
                db_path=self.db_path, connection=self._managed_connection
            )

    @property
    def seller_history(self) -> SellerHistoryRepository:
        return self._seller_repo

    @property
    def brand_history(self) -> BrandHistoryRepository:
        return self._brand_repo

    @property
    def case_history(self) -> CaseHistoryRepository:
        return self._case_repo

    def record_investigation(
        self,
        case_record: CaseHistoryRecord,
        seller_record: Optional[SellerHistoryRecord] = None,
        brand_record: Optional[BrandHistoryRecord] = None,
    ) -> None:
        logger.info(
            f"Recording investigation memory for case ID '{case_record.case_id}'."
        )
        self.case_history.save(case_record)
        if seller_record:
            self.seller_history.save(seller_record)
        if brand_record:
            self.brand_history.save(brand_record)

    def reset(self) -> None:
        """Reset memory by dropping and re-initializing all SQLite tables if using managed DB connection."""
        if self._managed_connection:
            with self._managed_connection as conn:
                conn.execute("DROP TABLE IF EXISTS seller_history_memory")
                conn.execute("DROP TABLE IF EXISTS brand_history_memory")
                conn.execute("DROP TABLE IF EXISTS case_history_memory")
            if hasattr(self._seller_repo, "_init_db"):
                self._seller_repo._init_db()  # type: ignore
            if hasattr(self._brand_repo, "_init_db"):
                self._brand_repo._init_db()  # type: ignore
            if hasattr(self._case_repo, "_init_db"):
                self._case_repo._init_db()  # type: ignore
        else:
            logger.warning(
                "Reset called on custom injected repositories without managed connection."
            )

    def close(self) -> None:
        if self._managed_connection:
            self._managed_connection.close()
            self._managed_connection = None


# Alias for explicitly indicating SQLite storage capability
SQLiteMemoryStore = MemoryStore
