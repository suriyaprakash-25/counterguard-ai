from backend.agents.intelligence_agents import (
    AuthorizedSellerAgent,
    BrandIntelligenceAgent,
    MetadataIntelligenceAgent,
    SpecificationValidationAgent,
)
from backend.collaboration.models.context import InvestigationContext
from backend.orchestrator.builder import build_graph
from backend.schemas.scraping import ParsedListing, ScrapingResult


def create_mock_state(
    title="Sony WH-1000XM5 Headphones",
    brand="Sony",
    seller="Official Sony Store",
    price=399.99,
    description="High quality headphones.",
):
    ctx = InvestigationContext(investigation_id="test_intel_inv")
    listing = ParsedListing(
        title=title,
        brand=brand,
        seller_name=seller,
        price=price,
        description=description,
        marketplace="Amazon",
    )
    scraping_res = ScrapingResult(success=True, listing=listing)
    return {"context": ctx, "scraping_result": scraping_res, "request": None}


def test_brand_intelligence_agent():
    agent = BrandIntelligenceAgent()
    state = create_mock_state(
        title="Sony WH-1000XM5 Wireless Noise Canceling Headphones", brand="Sony"
    )

    res = agent.run(state)

    assert "brand_intelligence" in res
    assert "context" in res

    ctx = res["context"]
    assert len(ctx.shared_evidence) == 1
    ev = ctx.shared_evidence[0]
    assert ev.agent_name == "BrandIntelligenceAgent"
    assert ev.category.upper() == "BRAND"
    assert ev.severity in ["critical", "high", "medium", "low", "info"]


def test_specification_validation_agent_impossible_specs():
    agent = SpecificationValidationAgent()
    # State with impossible specs: Bluetooth 9.0 and 10000mAh earbud battery
    state = create_mock_state(
        title="Super Earbuds Bluetooth 9.0 10000mAh Earbud Battery ANC",
        description="Revolutionary earbuds with Bluetooth 9.0 technology and 10000mAh earbud battery capacity.",
    )

    res = agent.run(state)

    assert "spec_validation" in res
    spec_result = res["spec_validation"]

    # Impossible specs should be flagged and risk score elevated to >= 85
    assert len(spec_result.impossible_specs) > 0
    assert spec_result.risk_score >= 85

    ctx = res["context"]
    assert len(ctx.shared_evidence) == 1
    ev = ctx.shared_evidence[0]
    assert ev.agent_name == "SpecificationValidationAgent"
    assert ev.category.upper() == "SPECIFICATION"
    assert ev.severity == "critical"


def test_authorized_seller_agent_official_seller():
    agent = AuthorizedSellerAgent()
    state = create_mock_state(seller="Sony Official Outlet Store")

    res = agent.run(state)

    assert "authorized_seller" in res
    ctx = res["context"]
    assert len(ctx.shared_evidence) == 1
    ev = ctx.shared_evidence[0]
    assert ev.agent_name == "AuthorizedSellerAgent"
    assert ev.category.upper() == "SELLER"


def test_metadata_intelligence_agent_keyword_stuffing():
    agent = MetadataIntelligenceAgent()
    # State with all caps title and repeated keyword stuffing
    stuffed_desc = "headphones " * 50
    state = create_mock_state(
        title="SONY WH-1000XM5 WIRELESS HEADPHONES BEST DEAL", description=stuffed_desc
    )

    res = agent.run(state)

    assert "metadata_intelligence" in res
    meta_result = res["metadata_intelligence"]

    assert meta_result.spam_score >= 50 or meta_result.keyword_stuffing_detected
    assert meta_result.risk_score >= 50

    ctx = res["context"]
    assert len(ctx.shared_evidence) == 1
    ev = ctx.shared_evidence[0]
    assert ev.agent_name == "MetadataIntelligenceAgent"
    assert ev.category.upper() == "METADATA"


def test_langgraph_orchestrator_builds_with_new_nodes():
    graph = build_graph()
    app = graph.compile()

    assert app is not None
    # Verify graph contains the new nodes
    nodes = list(app.get_graph().nodes.keys())
    assert "brand_intel" in nodes
    assert "spec_validation" in nodes
    assert "authorized_seller" in nodes
    assert "metadata_intel" in nodes
