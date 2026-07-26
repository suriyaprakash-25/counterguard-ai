from datetime import datetime, timezone

import pytest

from backend.memory import (
    BrandHistoryRecord,
    BrandHistoryRepository,
    CaseHistoryRecord,
    CaseHistoryRepository,
    MemoryStore,
    MemoryStoreInterface,
    SellerHistoryRecord,
    SellerHistoryRepository,
    SQLiteBrandHistoryRepository,
    SQLiteCaseHistoryRepository,
    SQLiteSellerHistoryRepository,
)


def test_interfaces_cannot_be_instantiated():
    with pytest.raises(TypeError):
        SellerHistoryRepository()
    with pytest.raises(TypeError):
        BrandHistoryRepository()
    with pytest.raises(TypeError):
        CaseHistoryRepository()
    with pytest.raises(TypeError):
        MemoryStoreInterface()


# -------------------------------------------------------------------------
# Seller History Repository Tests
# -------------------------------------------------------------------------
@pytest.fixture
def seller_repo():
    repo = SQLiteSellerHistoryRepository(db_path=":memory:")
    yield repo
    repo.close()


def test_seller_history_crud(seller_repo):
    rec = SellerHistoryRecord(
        id="mem-sel-100",
        seller_id="SELL_01",
        seller_name="Verified Electronics",
        marketplace="amazon",
        trust_score=88.5,
        verified_merchant=True,
    )

    # Save and get_by_id
    seller_repo.save(rec)
    fetched = seller_repo.get_by_id("mem-sel-100")
    assert fetched is not None
    assert fetched.seller_id == "SELL_01"
    assert fetched.trust_score == 88.5

    # get_by_seller_id without marketplace filter
    by_seller = seller_repo.get_by_seller_id("SELL_01")
    assert len(by_seller) == 1
    assert by_seller[0].id == "mem-sel-100"

    # get_by_seller_id with marketplace filter
    assert len(seller_repo.get_by_seller_id("SELL_01", marketplace="amazon")) == 1
    assert len(seller_repo.get_by_seller_id("SELL_01", marketplace="ebay")) == 0

    # list_all
    all_recs = seller_repo.list_all()
    assert len(all_recs) == 1

    # Delete
    seller_repo.delete("mem-sel-100")
    assert seller_repo.get_by_id("mem-sel-100") is None


# -------------------------------------------------------------------------
# Brand History Repository Tests
# -------------------------------------------------------------------------
@pytest.fixture
def brand_repo():
    repo = SQLiteBrandHistoryRepository(db_path=":memory:")
    yield repo
    repo.close()


def test_brand_history_crud(brand_repo):
    rec = BrandHistoryRecord(
        id="mem-brd-200",
        brand_name="Nike",
        trademark_reg_number="TM-123456",
        authorized_distributors=["Official Nike Shop", "Sports Direct"],
        total_cases_investigated=5,
    )

    brand_repo.save(rec)

    fetched = brand_repo.get_by_id("mem-brd-200")
    assert fetched is not None
    assert fetched.brand_name == "Nike"
    assert "Sports Direct" in fetched.authorized_distributors

    # Case insensitive lookup
    by_name = brand_repo.get_by_brand_name("nike  ")
    assert len(by_name) == 1
    assert by_name[0].total_cases_investigated == 5

    assert len(brand_repo.list_all()) == 1

    brand_repo.delete("mem-brd-200")
    assert brand_repo.get_by_id("mem-brd-200") is None


# -------------------------------------------------------------------------
# Case History Repository Tests
# -------------------------------------------------------------------------
@pytest.fixture
def case_repo():
    repo = SQLiteCaseHistoryRepository(db_path=":memory:")
    yield repo
    repo.close()


def test_case_history_crud(case_repo):
    rec = CaseHistoryRecord(
        case_id="CASE_2026_001",
        listing_id="LISTING_999",
        seller_id="SELL_01",
        brand_name="Apple",
        verdict="COUNTERFEIT",
        risk_score=94.2,
        action_taken="LEGAL_NOTICE_GENERATED",
        investigation_timestamp=datetime.now(timezone.utc),
    )

    case_repo.save(rec)

    fetched = case_repo.get_by_case_id("CASE_2026_001")
    assert fetched is not None
    assert fetched.verdict == "COUNTERFEIT"
    assert fetched.risk_score == 94.2

    # Query by listing_id and seller_id
    by_listing = case_repo.get_by_listing_id("LISTING_999")
    assert len(by_listing) == 1

    by_seller = case_repo.get_by_seller_id("SELL_01")
    assert len(by_seller) == 1

    assert len(case_repo.list_recent(limit=10)) == 1

    case_repo.delete("CASE_2026_001")
    assert case_repo.get_by_case_id("CASE_2026_001") is None


# -------------------------------------------------------------------------
# Unified Memory Store Tests
# -------------------------------------------------------------------------
def test_memory_store_orchestration():
    store = MemoryStore(db_path=":memory:")
    assert isinstance(store.seller_history, SellerHistoryRepository)
    assert isinstance(store.brand_history, BrandHistoryRepository)
    assert isinstance(store.case_history, CaseHistoryRepository)

    case_rec = CaseHistoryRecord(
        case_id="CASE_ORCH_101",
        listing_id="L_888",
        seller_id="S_888",
        brand_name="Rolex",
        verdict="SUSPICIOUS",
        risk_score=65.0,
    )
    seller_rec = SellerHistoryRecord(
        id="SEL_MEM_101",
        seller_id="S_888",
        seller_name="Discount Luxuries",
        trust_score=40.0,
    )
    brand_rec = BrandHistoryRecord(
        id="BRD_MEM_101",
        brand_name="Rolex",
        total_cases_investigated=12,
    )

    # Simultaneous recording
    store.record_investigation(
        case_record=case_rec,
        seller_record=seller_rec,
        brand_record=brand_rec,
    )

    assert store.case_history.get_by_case_id("CASE_ORCH_101") is not None
    assert store.seller_history.get_by_id("SEL_MEM_101") is not None
    assert len(store.brand_history.get_by_brand_name("Rolex")) == 1

    # Reset tables and verify all histories are empty while schemas remain operable
    store.reset()
    assert store.case_history.get_by_case_id("CASE_ORCH_101") is None
    assert store.seller_history.get_by_id("SEL_MEM_101") is None
    assert len(store.brand_history.get_by_brand_name("Rolex")) == 0

    store.close()
