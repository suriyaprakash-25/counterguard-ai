from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.main import app
from backend.database.engine import _set_sqlite_pragma, get_db_session
from backend.models import Base, EvidenceModel, InvestigationModel, ReportModel
from backend.schemas.investigation import InvestigationReport


@pytest.fixture
def client_and_session():
    """
    Test client and in-memory SQLite database session fixture with foreign keys enabled.
    Uses StaticPool to ensure the same in-memory DB is shared across sessions during tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _set_sqlite_pragma)
    Base.metadata.create_all(engine)
    SessionMaker = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionMaker()

    def override_get_db_session():
        db = SessionMaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)
    try:
        yield client, session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        app.dependency_overrides.clear()


def test_list_investigations_empty(client_and_session):
    client, _ = client_and_session
    response = client.get("/api/v1/investigations")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 0
    assert data["items"] == []
    assert data["total_pages"] == 0


def test_list_investigations_pagination_filtering_and_sorting(client_and_session):
    client, session = client_and_session

    # Populate DB with test investigations (inv1 is newest so it appears on page 1 in default desc order)
    inv1 = InvestigationModel(
        id="inv-1",
        listing_url="https://amazon.com/dp/B001",
        marketplace="Amazon",
        status="completed",
        created_at=datetime(2026, 7, 25, 12, 0, 0),
    )
    inv2 = InvestigationModel(
        id="inv-2",
        listing_url="https://amazon.com/dp/B002",
        marketplace="Amazon",
        status="in_progress",
        created_at=datetime(2026, 7, 25, 11, 0, 0),
    )
    inv3 = InvestigationModel(
        id="inv-3",
        listing_url="https://ebay.com/itm/999",
        marketplace="eBay",
        status="completed",
        created_at=datetime(2026, 7, 25, 10, 0, 0),
    )
    session.add_all([inv1, inv2, inv3])

    # Add a report to inv1 to test rich summary attributes
    report = ReportModel.from_pydantic(
        InvestigationReport(
            summary="High risk listing detected.",
            product="Luxury Sunglass",
            marketplace="Amazon",
            seller="SuspiciousVendor",
            price=49.99,
            risk_score=85,
            risk_level="HIGH",
            evidence_summary={},
            findings=["Logo misalignment."],
            recommendation="Issue takedown request.",
            confidence=94.0,
            ai_summary="",
            ai_reasoning="",
            investigation_timestamp="2026-07-25T10:05:00Z",
        ),
        investigation_id="inv-1",
    )
    session.add(report)
    session.commit()

    # 1. Test pagination (page=1, page_size=2)
    res_page = client.get("/api/v1/investigations?page=1&page_size=2")
    assert res_page.status_code == 200
    data_page = res_page.json()
    assert data_page["total_count"] == 3
    assert len(data_page["items"]) == 2
    assert data_page["total_pages"] == 2

    # Verify report enrichment on inv-1
    inv1_item = next(item for item in data_page["items"] if item["id"] == "inv-1")
    assert inv1_item["product"] == "Luxury Sunglass"
    assert inv1_item["risk_level"] == "HIGH"
    assert inv1_item["risk_score"] == 85

    # 2. Test marketplace filtering
    res_amz = client.get("/api/v1/investigations?marketplace=Amazon")
    assert res_amz.status_code == 200
    assert res_amz.json()["total_count"] == 2

    # 3. Test status filtering
    res_status = client.get("/api/v1/investigations?status=in_progress")
    assert res_status.status_code == 200
    assert res_status.json()["total_count"] == 1

    # 4. Test custom sorting (sort by marketplace ASC)
    res_sort = client.get("/api/v1/investigations?sort_by=marketplace&sort_order=asc")
    assert res_sort.status_code == 200
    sorted_items = res_sort.json()["items"]
    assert sorted_items[0]["marketplace"] == "Amazon"
    assert sorted_items[2]["marketplace"] == "eBay"


def test_get_investigation_detail_and_not_found(client_and_session):
    client, session = client_and_session

    inv = InvestigationModel(
        id="test-detail-id",
        listing_url="https://amazon.com/dp/B111222",
        marketplace="Amazon",
        status="completed",
    )
    session.add(inv)

    ev = EvidenceModel(
        investigation_id="test-detail-id",
        agent="scout",
        action="scraped",
        detail="Scraped product page successfully.",
        confidence_delta=5.0,
        timestamp="2026-07-25T14:00:00Z",
    )
    session.add(ev)
    session.commit()

    # 1. Query successful detail view
    res = client.get("/api/v1/investigations/test-detail-id")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "test-detail-id"
    assert len(data["evidence_timeline"]) == 1
    assert data["evidence_timeline"][0]["agent"] == "scout"

    # 2. Query non-existent ID -> 404
    res_404 = client.get("/api/v1/investigations/non-existent-id")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()


def test_delete_investigation_endpoint(client_and_session):
    client, session = client_and_session

    inv = InvestigationModel(
        id="to-delete-id",
        listing_url="https://ebay.com/itm/12345",
        marketplace="eBay",
        status="completed",
    )
    session.add(inv)
    session.commit()

    # 1. Execute successful deletion
    res_del = client.delete("/api/v1/investigations/to-delete-id")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True
    assert res_del.json()["id"] == "to-delete-id"

    # 2. Verify record removal (subsequent get returns 404)
    res_get = client.get("/api/v1/investigations/to-delete-id")
    assert res_get.status_code == 404

    # 3. Deleting non-existent ID returns 404
    res_del_404 = client.delete("/api/v1/investigations/to-delete-id")
    assert res_del_404.status_code == 404
