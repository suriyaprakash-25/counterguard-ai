import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from backend.database.engine import _set_sqlite_pragma
from backend.database.repositories import (
    EvidenceRepository,
    InvestigationRepository,
    ReportRepository,
)
from backend.models import Base, EvidenceModel, InvestigationModel, ReportModel
from backend.schemas.investigation import InvestigationReport


@pytest.fixture
def db_session():
    """
    In-memory SQLite session fixture for unit testing repositories and models.
    Enforces SQLite foreign key constraints identical to PostgreSQL behavior.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    event.listen(engine, "connect", _set_sqlite_pragma)
    Base.metadata.create_all(engine)
    SessionMaker = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionMaker()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_investigation_repository_crud(db_session):
    repo = InvestigationRepository(db_session)

    # 1. Create Investigation
    inv = InvestigationModel(
        listing_url="https://amazon.com/dp/B08X922ABC",
        marketplace="Amazon",
        status="pending",
    )
    saved_inv = repo.add(inv)
    assert saved_inv.id is not None
    assert saved_inv.listing_url == "https://amazon.com/dp/B08X922ABC"
    assert saved_inv.status == "pending"

    # 2. Get by ID
    fetched_inv = repo.get_by_id(saved_inv.id)
    assert fetched_inv is not None
    assert fetched_inv.id == saved_inv.id

    # 3. Update status
    updated_inv = repo.update_status(saved_inv.id, "completed")
    assert updated_inv is not None
    assert updated_inv.status == "completed"

    # 4. Get all
    inv2 = InvestigationModel(
        listing_url="https://ebay.com/itm/123456789",
        marketplace="eBay",
        status="completed",
    )
    repo.add(inv2)
    all_invs = repo.get_all(limit=10)
    assert len(all_invs) == 2

    # 5. Delete
    delete_result = repo.delete(saved_inv.id)
    assert delete_result is True
    assert repo.get_by_id(saved_inv.id) is None
    assert repo.delete("non_existent_id") is False


def test_evidence_repository_crud(db_session):
    inv_repo = InvestigationRepository(db_session)
    ev_repo = EvidenceRepository(db_session)

    inv = InvestigationModel(
        listing_url="https://aliexpress.com/item/99999.html",
        marketplace="AliExpress",
        status="in_progress",
    )
    inv_repo.add(inv)

    # 1. Add single evidence item
    ev1 = EvidenceModel(
        investigation_id=inv.id,
        agent="scout",
        action="discovered_listing",
        detail="Listing scraped successfully.",
        confidence_delta=10.0,
        timestamp="2026-07-25T10:00:00Z",
    )
    saved_ev1 = ev_repo.add(ev1)
    assert saved_ev1.id is not None
    assert ev_repo.get_by_id(saved_ev1.id) is not None

    # 2. Add batch evidence items
    ev2 = EvidenceModel(
        investigation_id=inv.id,
        agent="visual_forensics",
        action="analyzed_images",
        detail="Low image similarity vs golden reference.",
        confidence_delta=35.0,
        timestamp="2026-07-25T10:01:00Z",
    )
    ev3 = EvidenceModel(
        investigation_id=inv.id,
        agent="price_anomaly",
        action="analyzed_price",
        detail="Statistical pricing outlier detected (75% below median).",
        confidence_delta=30.0,
        timestamp="2026-07-25T10:02:00Z",
    )
    saved_batch = ev_repo.add_batch([ev2, ev3])
    assert len(saved_batch) == 2

    # 3. Get by investigation ID
    all_ev = ev_repo.get_by_investigation(inv.id)
    assert len(all_ev) == 3
    assert all_ev[0].agent == "scout"
    assert all_ev[2].agent == "price_anomaly"

    # 4. Delete by investigation ID
    deleted_count = ev_repo.delete_by_investigation(inv.id)
    assert deleted_count == 3
    assert len(ev_repo.get_by_investigation(inv.id)) == 0


def test_report_repository_crud_and_pydantic_mapping(db_session):
    inv_repo = InvestigationRepository(db_session)
    report_repo = ReportRepository(db_session)

    inv = InvestigationModel(
        listing_url="https://amazon.com/dp/B000TEST01",
        marketplace="Amazon",
        status="completed",
    )
    inv_repo.add(inv)

    sample_schema = InvestigationReport(
        summary="Counterfeit risk identified across multiple specialist analyses.",
        product="UltraSound Pro Headphones",
        marketplace="Amazon",
        seller="GenericAudioTech",
        price=29.99,
        risk_score=88,
        risk_level="HIGH",
        evidence_summary={
            "visual": {"similarity": "0.42"},
            "price": {"outlier": "true"},
        },
        findings=[
            "Logo inconsistency detected in secondary pictures.",
            "Price anomaly > 3 std devs below catalog value.",
        ],
        recommendation="Draft legal takedown notice for manual verification.",
        confidence=91.5,
        ai_summary="AI found conclusive cross-validated discrepancies.",
        ai_reasoning="Graph agent confirmed seller linked to previously suspended network.",
        investigation_timestamp="2026-07-25T14:30:00Z",
    )

    # 1. Map from Pydantic schema to ReportModel DB entity and add
    report_model = ReportModel.from_pydantic(sample_schema, investigation_id=inv.id)
    saved_report = report_repo.add(report_model)
    assert saved_report.id is not None
    assert saved_report.investigation_id == inv.id

    # 2. Get by investigation ID
    fetched_report = report_repo.get_by_investigation(inv.id)
    assert fetched_report is not None
    assert fetched_report.product == "UltraSound Pro Headphones"

    # 3. Verify helper methods and reverse mapping to Pydantic schema
    ev_dict = fetched_report.get_evidence_summary_dict()
    assert ev_dict["visual"]["similarity"] == "0.42"
    findings_list = fetched_report.get_findings_list()
    assert len(findings_list) == 2

    reconstructed_schema = fetched_report.to_pydantic()
    assert reconstructed_schema.summary == sample_schema.summary
    assert reconstructed_schema.risk_score == sample_schema.risk_score
    assert reconstructed_schema.evidence_summary == sample_schema.evidence_summary

    # 4. Delete report
    assert report_repo.delete(saved_report.id) is True
    assert report_repo.get_by_id(saved_report.id) is None


def test_cascade_deletion(db_session):
    inv_repo = InvestigationRepository(db_session)
    ev_repo = EvidenceRepository(db_session)
    report_repo = ReportRepository(db_session)

    inv = InvestigationModel(
        listing_url="https://ebay.com/itm/888888",
        marketplace="eBay",
        status="completed",
    )
    inv_repo.add(inv)

    ev = EvidenceModel(
        investigation_id=inv.id,
        agent="scout",
        action="discovered_listing",
        detail="Initial listing observation.",
        confidence_delta=5.0,
        timestamp="2026-07-25T15:00:00Z",
    )
    ev_repo.add(ev)

    sample_schema = InvestigationReport(
        summary="Moderate risk.",
        product="Watch Strap",
        marketplace="eBay",
        seller="WatchBandPlus",
        price=15.00,
        risk_score=45,
        risk_level="MODERATE",
        evidence_summary={},
        findings=["Minor packaging discrepancy."],
        recommendation="Monitor seller activity.",
        confidence=65.0,
        ai_summary="",
        ai_reasoning="",
        investigation_timestamp="2026-07-25T15:05:00Z",
    )
    report_model = ReportModel.from_pydantic(sample_schema, investigation_id=inv.id)
    report_repo.add(report_model)

    assert ev_repo.get_by_id(ev.id) is not None
    assert report_repo.get_by_investigation(inv.id) is not None

    # Deleting the investigation entity should cleanly cascade to evidence and reports
    inv_repo.delete(inv.id)

    assert ev_repo.get_by_id(ev.id) is None
    assert report_repo.get_by_investigation(inv.id) is None
