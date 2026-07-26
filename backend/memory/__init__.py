"""
CounterGuard Reusable Memory Layer.

Provides independent, persistent historical memory tracking for Sellers, Brands, and Investigation Cases.
Uses repository abstractions and SQLite storage implementations without any LangGraph or AI reasoning dependencies.
"""

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
from backend.memory.memory_store import (
    MemoryStore,
    MemoryStoreInterface,
    SQLiteMemoryStore,
)
from backend.memory.seller_history import (
    SellerHistoryRecord,
    SellerHistoryRepository,
    SQLiteSellerHistoryRepository,
)

__all__ = [
    # Interfaces
    "SellerHistoryRepository",
    "BrandHistoryRepository",
    "CaseHistoryRepository",
    "MemoryStoreInterface",
    # Data Models
    "SellerHistoryRecord",
    "BrandHistoryRecord",
    "CaseHistoryRecord",
    # Implementations
    "SQLiteSellerHistoryRepository",
    "SQLiteBrandHistoryRepository",
    "SQLiteCaseHistoryRepository",
    "MemoryStore",
    "SQLiteMemoryStore",
]
