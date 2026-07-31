from backend.agents.reference_discovery_agent import (
    ReferenceDiscoveryAgent,
    reference_discovery_node,
)
from backend.agents.reference_extraction_agent import (
    ReferenceExtractionAgent,
    reference_extraction_node,
)
from backend.agents.trusted_product_agent import TrustedProductAgent
from backend.orchestrator.builder import build_graph
from backend.schemas.canonical_product import CanonicalProductKnowledge
from backend.schemas.investigation import InvestigationRequest
from backend.services.investigation_service import InvestigationService
from backend.state import InvestigationState


def test_langgraph_compilation_with_reference_intelligence():
    """Verifies that LangGraph StateGraph compiles cleanly with reference intelligence nodes."""
    builder = build_graph()
    compiled_graph = builder.compile()

    node_names = set(compiled_graph.nodes.keys())
    assert "reference_discovery" in node_names
    assert "reference_extraction" in node_names
    assert "trusted_product" in node_names
    assert len(node_names) >= 15


def test_reference_discovery_and_extraction_nodes_execution():
    """Verifies sequential execution of discovery and extraction nodes."""
    state: InvestigationState = {
        "request": InvestigationRequest(
            listing_url="https://nothing.tech/products/phone-2a",
            marketplace="Nothing Store",
            target_value="Nothing Phone (2a)",
        ),
        "analysis": type(
            "MockAnalysis",
            (),
            {"brand": "Nothing", "title": "Nothing Phone (2a)", "price": 23999.0},
        )(),
    }

    disc_update = reference_discovery_node(state)
    assert disc_update["reference_status"] in ("discovered", "fallback_legacy")

    # Combine state with discovery updates
    state.update(disc_update)
    ext_update = reference_extraction_node(state)

    if disc_update["reference_status"] == "discovered":
        assert ext_update["canonical_product_knowledge"] is not None
        cpk: CanonicalProductKnowledge = ext_update["canonical_product_knowledge"]
        assert cpk.brand == "Nothing"
        assert cpk.canonical_id == "nothing-nothing-phone-2a"
        assert ext_update["reference_confidence"] > 0.0


def test_fallback_behavior_on_unverified_discovery():
    """Verifies resilient fallback when discovery returns unverified source."""
    agent = ReferenceDiscoveryAgent()
    state: InvestigationState = {
        "analysis": type(
            "MockAnalysis",
            (),
            {"brand": "Unknown Fake Brand XYZ", "title": "Generic Unbranded Item 999"},
        )()
    }

    disc_update = agent.run(state)
    assert disc_update["verified_source"] is None
    assert disc_update["reference_discovery_metadata"]["fallback_engaged"] is True
    assert disc_update["reference_status"] == "fallback_legacy"

    # Test extraction handling of missing source
    state.update(disc_update)
    ext_agent = ReferenceExtractionAgent()
    ext_update = ext_agent.run(state)

    assert ext_update["canonical_product_knowledge"] is None
    assert ext_update["reference_extraction_metadata"]["fallback_engaged"] is True

    # Test legacy TrustedProductAgent fallback handling
    state.update(ext_update)
    trusted_agent = TrustedProductAgent()
    trusted_update = trusted_agent.run(state)
    assert trusted_update["trusted_product_result"] is not None


def test_e2e_investigation_service_reference_intelligence():
    """Executes full end-to-end investigation engine with Reference Intelligence enabled."""
    service = InvestigationService()
    req = InvestigationRequest(
        listing_url="https://www.flipkart.com/p/itm123",
        marketplace="Flipkart",
        target_value="CMF Buds",
    )

    report = service.run_investigation(req)
    assert report is not None
    assert report.risk_score >= 0
    assert report.risk_level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    assert report.product is not None
