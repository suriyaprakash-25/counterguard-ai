"""
Tests for Sprint 3 Preliminary Refinements:
  1. Discovery Memory (Cache loading, diffs, provenance updates)
  2. Marketplace Health Scores (Matrix retrieval & metrics)
  3. Multi-Stage Discovery Confidence (search, matching, discovery confidence)
  4. Discovery Provenance Lineage (discovered_via & provenance_chain)
  5. Priority Investigation Queue (Critical -> High -> Medium -> Low dispatch ordering)
"""
from unittest.mock import MagicMock, patch

from backend.discovery.marketplace_health import MarketplaceHealthService
from backend.discovery.memory import DiscoveryMemoryService
from backend.discovery.parallel_launcher import ParallelInvestigationLauncher
from backend.schemas.discovery import (
    DiscoverySearchResponse,
    ListingCandidate,
)
from backend.schemas.parallel_launch import CandidateLaunchItem, ParallelLaunchRequest


def test_refinement_1_discovery_memory_caching():
    DiscoveryMemoryService.clear()

    candidate = ListingCandidate(
        title="Memory Cache Product Test",
        url="https://amazon.in/dp/B001",
        marketplace="Amazon",
    )
    dummy_resp = DiscoverySearchResponse(
        query="Memory Cache Product Test",
        normalized_query="Memory Cache Product Test",
        marketplaces_searched=["Amazon"],
        candidates=[candidate],
        listing_groups=[],
        top_investigation_targets=[],
        metadata={"candidate_count": 1},
    )

    # Store in memory
    DiscoveryMemoryService.put("Memory Cache Product Test", dummy_resp)

    # Fetch from memory
    cached = DiscoveryMemoryService.get("Memory Cache Product Test")
    assert cached is not None
    assert cached.metadata.get("from_memory") is True
    assert cached.candidates[0].discovered_via == "Historical Memory"
    assert (
        "Historical Memory: Loaded from cache" in cached.candidates[0].provenance_chain
    )

    # Clear memory cache to isolate other tests
    DiscoveryMemoryService.clear()


def test_refinement_2_marketplace_health_scores():
    health_list = MarketplaceHealthService.get_all_health_scores()
    assert len(health_list) >= 6

    amazon_health = MarketplaceHealthService.get_health("Amazon")
    assert amazon_health.health_score == 98
    assert amazon_health.status == "Operational"

    meesho_health = MarketplaceHealthService.get_health("Meesho")
    assert meesho_health.health_score == 72


def test_refinement_3_and_4_discovery_confidence_and_provenance():
    candidate = ListingCandidate(
        title="Nothing Phone 3 Original",
        url="https://flipkart.com/p/123",
        marketplace="Flipkart",
        search_confidence=0.92,
        matching_confidence=0.88,
        discovery_confidence=0.90,
        discovered_via="Marketplace API",
        provenance_chain=["Marketplace API: Flipkart", "Deduplication: Union-Find"],
    )

    assert candidate.search_confidence == 0.92
    assert candidate.matching_confidence == 0.88
    assert candidate.discovery_confidence == 0.90
    assert candidate.discovered_via == "Marketplace API"
    assert len(candidate.provenance_chain) == 2


def test_refinement_5_priority_investigation_queue():
    launcher = ParallelInvestigationLauncher()

    c1 = CandidateLaunchItem(
        candidate_id="c1",
        marketplace="TradeIndia",
        title="Low Priority Listing",
        url="https://tradeindia.com/1",
    )
    c2 = CandidateLaunchItem(
        candidate_id="c2",
        marketplace="Amazon",
        title="Critical Priority Listing",
        url="https://amazon.in/2",
    )

    req = ParallelLaunchRequest(
        candidates=[c1, c2],
        priority="critical",
    )

    with patch(
        "backend.discovery.parallel_launcher.InvestigationRepository"
    ) as mock_repo:
        with patch("backend.discovery.parallel_launcher.get_session_maker") as mock_sm:
            mock_db = MagicMock()
            mock_sm.return_value = lambda: mock_db

            # mock thread execution to avoid spawning real background threads
            with patch("threading.Thread") as mock_thread_cls:
                mock_t = MagicMock()
                mock_thread_cls.return_value = mock_t

                res = launcher.launch(req)
                assert res.total_launched == 2
                assert res.metadata.get("priority_queue_used") is True
                assert res.metadata.get("base_priority") == "CRITICAL"
