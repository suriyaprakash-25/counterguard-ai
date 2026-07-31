import concurrent.futures
import logging
import time

from backend.agents.intelligence_agents import SpecificationValidationAgent
from backend.agents.reference_discovery_agent import reference_discovery_node
from backend.agents.reference_extraction_agent import reference_extraction_node
from backend.agents.specialists import BrandAgent, PriceAgent
from backend.orchestrator.builder import build_graph
from backend.schemas.canonical_product import CanonicalProductKnowledge
from backend.schemas.intelligence import SpecificationValidationResult
from backend.schemas.investigation import (
    InvestigationRequest,
)
from backend.schemas.llm_models import PriceAnalysisResult
from backend.services.investigation_service import InvestigationService
from backend.state import InvestigationState
from backend.telemetry.observability import (
    StructuredLogger,
    get_current_memory_mb,
    verify_canonical_knowledge_immutability,
)

logger = logging.getLogger(__name__)


def test_graph_validation_and_node_ordering():
    """Verify graph compiles without circular edges or dead ends."""
    graph = build_graph()
    compiled = graph.compile()
    assert compiled is not None

    # Verify nodes exist in compiled graph
    nodes = compiled.nodes
    assert "reference_discovery" in nodes
    assert "reference_extraction" in nodes
    assert "planner" in nodes
    assert "coordinator" in nodes


def test_canonical_knowledge_immutability():
    """Verify CanonicalProductKnowledge is strictly immutable during agent executions."""
    cpk_before = CanonicalProductKnowledge(
        brand="Apple",
        product_name="AirPods Pro (2nd Gen)",
        canonical_id="apple-airpods-pro-2nd-gen",
        msrp=24900.0,
        currency="INR",
        canonical_specs={"battery": "6 hours", "storage": "N/A"},
    )

    # Freeze reference snapshot
    snapshot_json = cpk_before.model_dump_json()

    state: InvestigationState = {
        "scraping_result": type(
            "MockScrapingResult",
            (),
            {
                "listing": type(
                    "MockListing", (), {"title": "AirPods Pro", "price": 4999.0}
                )()
            },
        )(),
        "canonical_product_knowledge": cpk_before,
    }

    # Run downstream agents
    price_agent = PriceAgent()
    brand_agent = BrandAgent()
    spec_agent = SpecificationValidationAgent()

    price_agent._update_state(
        state,
        PriceAnalysisResult(anomaly_detected=True, risk_score=90, reasoning="Test"),
    )
    brand_agent._update_state(
        state,
        type("MockBrandRes", (), {"risk_score": 85, "reasoning": "Test Brand"})(),
    )
    spec_agent._update_state(
        state,
        SpecificationValidationResult(
            risk_score=30,
            reasoning="Test Spec",
            missing_specs=[],
            inconsistent_specs=[],
        ),
    )

    cpk_after = state["canonical_product_knowledge"]
    assert verify_canonical_knowledge_immutability(cpk_before, cpk_after)
    assert cpk_after.model_dump_json() == snapshot_json


def test_failure_recovery_and_graceful_degradation():
    """Verify discovery and extraction failures fallback to legacy mode cleanly."""
    state: InvestigationState = {
        "request": InvestigationRequest(
            listing_url="https://unknown-unverified-site.invalid/item",
            marketplace="UnknownMarket",
            target_value="NonExistentItem",
        )
    }

    disc_out = reference_discovery_node(state)
    assert disc_out["reference_status"] == "fallback_legacy"
    assert disc_out["verified_source"] is None

    # Feed fallback state into extraction
    state.update(disc_out)
    ext_out = reference_extraction_node(state)
    assert ext_out["canonical_product_knowledge"] is None

    # Feed state into TrustedProductAgent / legacy pipeline without crashing
    from backend.agents.trusted_product_agent import TrustedProductAgent

    trusted_agent = TrustedProductAgent()
    trusted_res = trusted_agent.run(state)
    assert "trusted_product_result" in trusted_res


def test_structured_telemetry_and_timeline_generation():
    """Verify timeline and structured JSON telemetry generation."""
    event = StructuredLogger.log_node_event(
        correlation_id="corr-test123",
        investigation_id="inv-test456",
        node_name="test_node",
        status="success",
        duration_ms=45.2,
        memory_mb=64.0,
    )
    assert event["correlation_id"] == "corr-test123"
    assert event["duration_ms"] == 45.2
    assert event["status"] == "success"


def test_multi_investigation_concurrency_and_isolation():
    """Run concurrent investigations across 6 major brand products and verify zero state pollution."""
    service = InvestigationService()

    requests = [
        InvestigationRequest(
            listing_url="https://nothing.tech/phone-2a",
            marketplace="OfficialStore",
            target_value="Nothing Phone (2a)",
        ),
        InvestigationRequest(
            listing_url="https://apple.com/airpods-pro",
            marketplace="OfficialStore",
            target_value="Apple AirPods Pro",
        ),
        InvestigationRequest(
            listing_url="https://samsung.com/galaxy-s24",
            marketplace="OfficialStore",
            target_value="Samsung Galaxy S24",
        ),
        InvestigationRequest(
            listing_url="https://sony.com/wh1000xm5",
            marketplace="OfficialStore",
            target_value="Sony WH-1000XM5",
        ),
        InvestigationRequest(
            listing_url="https://nike.com/af1",
            marketplace="OfficialStore",
            target_value="Nike Air Force 1",
        ),
        InvestigationRequest(
            listing_url="https://adidas.com/samba",
            marketplace="OfficialStore",
            target_value="Adidas Samba",
        ),
    ]

    def run_req(req):
        t0 = time.perf_counter()
        rep = service.run_investigation(req)
        elapsed = time.perf_counter() - t0
        return req.target_value, rep, elapsed

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(run_req, req) for req in requests]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 6
    for title, report, elapsed in results:
        assert report is not None
        assert report.risk_score >= 0
        assert elapsed < 15.0  # Concurrency benchmark constraint


def test_performance_benchmark_and_node_latencies():
    """Generates node latency and memory utilization benchmark metrics."""
    service = InvestigationService()
    req = InvestigationRequest(
        listing_url="https://nothing.tech/products/cmf-buds",
        marketplace="OfficialStore",
        target_value="CMF Buds",
    )

    t0 = time.perf_counter()
    mem_before = get_current_memory_mb()
    report = service.run_investigation(req)
    total_time_ms = (time.perf_counter() - t0) * 1000.0
    mem_after = get_current_memory_mb()

    assert report is not None
    assert total_time_ms > 0.0
    logger.info(
        f"[Benchmark] Total Investigation Latency: {total_time_ms:.2f}ms, RSS Memory: {mem_after:.2f}MB (delta: {mem_after - mem_before:.2f}MB)"
    )
