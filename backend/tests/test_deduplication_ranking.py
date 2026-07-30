"""
Sprint 2.2 — Unit tests for Deduplication & Ranking Engine.
Tests cover:
  - Title Jaccard similarity clustering
  - Model number extraction and deduplication
  - Seller trust scoring
  - Price anomaly scoring
  - Metadata quality scoring
  - Listing completeness scoring
  - Full pipeline integration (dedup → rank → top targets)
  - API contract validation
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.discovery.deduplication import (
    DeduplicationService,
    _extract_model_numbers,
    _jaccard,
    _normalized_product_name,
    _titles_are_equivalent,
)
from backend.discovery.ranking import (
    RankingEngine,
    _listing_completeness_score,
    _marketplace_risk_score,
    _metadata_quality_score,
    _price_anomaly_score,
    _seller_trust_score,
)
from backend.discovery.service import DiscoveryService
from backend.schemas.discovery import DiscoverySearchRequest, ListingCandidate

# ── Helpers ───────────────────────────────────────────────────────────────────


def make_candidate(**kwargs) -> ListingCandidate:
    defaults = dict(
        title="Sony WH-1000XM5 Wireless Headphones",
        url="https://example.com/product",
        price=2999.0,
        seller="Amazon Official Flagship Store",
        marketplace="Amazon",
        confidence=0.90,
    )
    defaults.update(kwargs)
    return ListingCandidate(**defaults)


# ── Deduplication Unit Tests ──────────────────────────────────────────────────


def test_jaccard_identical_sets():
    a = {"sony", "wh1000xm5", "wireless"}
    assert _jaccard(a, a) == 1.0


def test_jaccard_disjoint_sets():
    a = {"sony", "xm5"}
    b = {"nike", "airmax"}
    assert _jaccard(a, b) == 0.0


def test_jaccard_partial_overlap():
    a = {"sony", "wh1000xm5", "wireless", "headphones"}
    b = {"sony", "wh1000xm5", "earbuds"}
    score = _jaccard(a, b)
    assert 0.3 < score < 0.7


def test_extract_model_numbers():
    title = "Sony WH-1000XM5 Wireless Active Noise Cancelling Headphones"
    models = _extract_model_numbers(title)
    assert any("1000" in m or "xm5" in m.lower() for m in models)


def test_titles_equivalent_same_product():
    t1 = "Sony WH-1000XM5 Wireless Headphones (Official Brand Listing)"
    t2 = "Sony WH-1000XM5 Wireless Headphones - Unauthorized Reseller"
    assert _titles_are_equivalent(t1, t2)


def test_titles_not_equivalent_different_product():
    t1 = "Sony WH-1000XM5 Wireless Headphones"
    t2 = "Nike Air Max 90 Running Shoes"
    assert not _titles_are_equivalent(t1, t2)


def test_deduplication_groups_same_product():
    svc = DeduplicationService()
    candidates = [
        make_candidate(
            title="CMF Buds 2a (Official Brand Listing)", marketplace="Amazon"
        ),
        make_candidate(title="CMF Buds 2a (Assured Authentic)", marketplace="Flipkart"),
        make_candidate(title="CMF Buds 2a Replica Master Copy", marketplace="Meesho"),
    ]
    groups = svc.deduplicate(candidates)
    assert len(groups) == 1
    assert groups[0].listing_count == 3
    assert "Amazon" in groups[0].unique_marketplaces
    assert "Flipkart" in groups[0].unique_marketplaces


def test_deduplication_separates_different_products():
    svc = DeduplicationService()
    candidates = [
        make_candidate(
            title="Sony WH-1000XM5 Wireless Headphones", marketplace="Amazon"
        ),
        make_candidate(title="Nike Air Max 90 Running Shoes", marketplace="Flipkart"),
        make_candidate(title="CMF Buds 2a Earbuds", marketplace="Myntra"),
    ]
    groups = svc.deduplicate(candidates)
    assert len(groups) == 3


def test_deduplication_price_range():
    svc = DeduplicationService()
    candidates = [
        make_candidate(
            title="Sony WH-1000XM5 Headphones", price=3000.0, marketplace="Amazon"
        ),
        make_candidate(
            title="Sony WH-1000XM5 Headphones Replica",
            price=500.0,
            marketplace="Meesho",
        ),
        make_candidate(
            title="Sony WH-1000XM5 Headphones Authentic",
            price=2800.0,
            marketplace="Flipkart",
        ),
    ]
    groups = svc.deduplicate(candidates)
    assert len(groups) == 1
    pr = groups[0].price_range
    assert pr["min"] == 500.0
    assert pr["max"] == 3000.0
    assert 1000.0 < pr["avg"] < 3000.0


def test_normalized_product_name():
    name = _normalized_product_name("CMF Buds 2a (Official Brand Listing)")
    assert "official" not in name.lower()
    assert "brand" not in name.lower()
    assert "cmf" in name.lower() or "Cmf" in name


# ── Ranking Unit Tests ────────────────────────────────────────────────────────


def test_price_anomaly_extreme_underpricing():
    # 70% below average → score should be 1.0 (max)
    score = _price_anomaly_score(make_candidate(price=300.0), group_avg=1000.0)
    assert score == 1.0


def test_price_anomaly_fair_price():
    # 5% below average → very low anomaly
    score = _price_anomaly_score(make_candidate(price=950.0), group_avg=1000.0)
    assert score < 0.20


def test_price_anomaly_zero_price():
    score = _price_anomaly_score(make_candidate(price=0.0), group_avg=1000.0)
    assert score == 0.6  # unknown price → medium risk


def test_seller_trust_official():
    score = _seller_trust_score("Amazon Official Flagship Store")
    assert score < 0.10


def test_seller_trust_replica():
    score = _seller_trust_score("Fashion Hub Wholesale Replica Combo Surat")
    assert score >= 0.75


def test_seller_trust_unknown():
    score = _seller_trust_score("TechStore XYZ 2024")
    assert 0.30 <= score <= 0.50


def test_marketplace_risk_scores():
    assert _marketplace_risk_score("Amazon") < _marketplace_risk_score("Meesho")
    assert _marketplace_risk_score("Meesho") < _marketplace_risk_score("TradeIndia")


def test_listing_completeness_all_present():
    c = make_candidate(
        price=999.0, thumbnail="http://img.com/p.jpg", availability="In Stock"
    )
    score = _listing_completeness_score(c)
    assert score < 0.25


def test_listing_completeness_missing_all():
    c = make_candidate(price=0.0, thumbnail=None, availability="")
    score = _listing_completeness_score(c)
    assert score >= 0.55


def test_metadata_quality_noisy_title():
    c = make_candidate(
        title="CMF Buds 2a Replica Master Copy OEM Bulk Wholesale Deal Combo Surat"
    )
    score = _metadata_quality_score(c)
    assert score >= 0.40


def test_metadata_quality_clean_title():
    c = make_candidate(title="Sony WH-1000XM5 Wireless Headphones")
    score = _metadata_quality_score(c)
    assert score < 0.20


def test_ranking_engine_orders_groups():
    engine = RankingEngine()
    svc = DeduplicationService()

    safe = make_candidate(
        title="Sony WH-1000XM5 Headphones",
        price=3000.0,
        seller="Amazon Official Flagship Store",
        marketplace="Amazon",
        thumbnail="http://img.com/p.jpg",
        availability="In Stock",
    )
    risky = make_candidate(
        title="Sony WH-1000XM5 Headphones Replica Master Copy",
        price=199.0,
        seller="Fashion Hub Wholesale Surat Replica OEM Combo",
        marketplace="Meesho",
        thumbnail=None,
        availability="",
    )

    groups = svc.deduplicate([safe, risky])
    ranked = engine.rank_groups(groups)

    assert len(ranked) >= 1
    # The group containing the risky listing should have a high priority score
    top_group = ranked[0]
    assert top_group.priority_score is not None
    assert top_group.priority_score.total_priority_score > 20.0


def test_ranking_investigation_priority_labels():
    engine = RankingEngine()
    svc = DeduplicationService()

    candidates = [
        make_candidate(
            title="Fake Replica OEM Bulk CMF Buds 2a",
            price=50.0,
            seller="Shenzhen OEM Wholesale Replica Hub",
            marketplace="Meesho",
            thumbnail=None,
            availability="",
        )
    ]
    groups = svc.deduplicate(candidates)
    ranked = engine.rank_groups(groups)
    assert ranked[0].investigation_priority in {"critical", "high", "normal", "low"}


def test_top_targets_selection():
    engine = RankingEngine()
    svc = DeduplicationService()

    candidates = [
        make_candidate(
            title="Sony WH-1000XM5 Official",
            price=3000.0,
            seller="Amazon Official Flagship Store",
            marketplace="Amazon",
        ),
        make_candidate(
            title="CMF Buds 2a Official",
            price=2999.0,
            seller="Flipkart Assured",
            marketplace="Flipkart",
        ),
    ]
    groups = svc.deduplicate(candidates)
    ranked = engine.rank_groups(groups)
    targets = engine.pick_top_targets(ranked, top_n=5)

    assert len(targets) <= 5
    assert all(t.url.startswith("http") for t in targets)


# ── Full Pipeline Integration Test ────────────────────────────────────────────


async def test_full_discovery_pipeline():
    svc = DiscoveryService()
    req = DiscoverySearchRequest(query="CMF Buds 2a", limit_per_marketplace=3)
    result = await svc.discover_products(req)

    assert result.normalized_query == "CMF Buds 2a"
    assert len(result.candidates) > 0
    assert len(result.listing_groups) > 0
    assert len(result.top_investigation_targets) > 0
    assert result.metadata["group_count"] <= result.metadata["candidate_count"]
    assert result.metadata["search_engine_version"] == "CounterGuard-Discovery-v2.2"

    # Every group must have a priority score
    for group in result.listing_groups:
        assert group.priority_score is not None
        assert 0.0 <= group.priority_score.total_priority_score <= 100.0
        assert group.investigation_priority in {"critical", "high", "normal", "low"}


# ── API Contract Tests ────────────────────────────────────────────────────────


def test_api_search_returns_groups_and_targets():
    client = TestClient(app)
    resp = client.post(
        "/api/v1/discovery/search",
        json={"query": "CMF Buds 2a", "limit_per_marketplace": 2},
    )
    assert resp.status_code == 200
    data = resp.json()

    # Sprint 2.1 backward compat
    assert "candidates" in data
    assert len(data["candidates"]) > 0

    # Sprint 2.2 new fields
    assert "listing_groups" in data
    assert len(data["listing_groups"]) > 0
    assert "top_investigation_targets" in data
    assert len(data["top_investigation_targets"]) > 0

    # Validate group schema
    group = data["listing_groups"][0]
    assert "group_id" in group
    assert "canonical_title" in group
    assert "listing_count" in group
    assert "priority_score" in group
    assert "investigation_priority" in group
    assert group["investigation_priority"] in {"critical", "high", "normal", "low"}

    ps = group["priority_score"]
    assert "total_priority_score" in ps
    assert "reasoning" in ps
    assert isinstance(ps["reasoning"], list)

    # Metadata Sprint 2.2
    meta = data["metadata"]
    assert "group_count" in meta
    assert "deduplication_reduction" in meta
    assert meta["search_engine_version"] == "CounterGuard-Discovery-v2.2"
