from backend.collaboration.models.context import InvestigationContext
from backend.memory.models.domain import Evidence
from backend.services.verdict_engine import VerdictEngine


def test_confidence_evolution_timeline_and_reasoning_steps():
    ctx = InvestigationContext(investigation_id="inv_conf_test")

    # Step 1: PlanningAgent
    ctx.record_confidence_step(
        agent_name="PlanningAgent",
        previous_confidence=0.40,
        current_confidence=0.42,
        reason="Initialized investigation strategy",
    )

    # Step 2: PriceAgent
    ctx.add_evidence(
        Evidence(
            evidence_id="ev-p1",
            agent_name="PriceAgent",
            category="PRICE",
            title="Price Anomaly",
            description="87% below MSRP",
            confidence=0.71,
            severity="critical",
        )
    )

    # Step 3: SellerAgent
    ctx.add_evidence(
        Evidence(
            evidence_id="ev-s2",
            agent_name="SellerAgent",
            category="SELLER",
            title="WHOIS Audit",
            description="Seller age 8 days",
            confidence=0.83,
            severity="high",
            derived_from=["ev-p1"],
        )
    )

    # Step 4: BrandIntelligenceAgent
    ctx.add_evidence(
        Evidence(
            evidence_id="ev-b3",
            agent_name="BrandIntelligenceAgent",
            category="BRAND",
            title="Brand Catalog Audit",
            description="Missing manufacturer branding metadata",
            confidence=0.88,
            severity="high",
            derived_from=["ev-s2"],
        )
    )

    # Assert Confidence Timeline Progression
    assert len(ctx.confidence_timeline) == 4
    assert ctx.confidence_timeline[0].agent == "PlanningAgent"
    assert ctx.confidence_timeline[1].agent == "PriceAgent"
    assert ctx.confidence_timeline[2].agent == "SellerAgent"
    assert ctx.confidence_timeline[3].agent == "BrandIntelligenceAgent"

    # Evaluate Risk with VerdictEngine
    verdict = VerdictEngine.evaluate_risk(
        raw_risk_score=82,
        product_name="Sony WH-1000XM5 Wireless Headphones",
        marketplace="Amazon",
        seller_name="Unverified Tech Deals",
        price=49.99,
        market_avg_price=399.99,
        context=ctx,
    )

    # Assert Structured Reasoning Timeline
    assert hasattr(verdict, "reasoning_timeline")
    assert hasattr(verdict, "evidence_graph")
    assert len(verdict.reasoning_timeline) >= 3
    assert verdict.reasoning_timeline[0]["sequence_number"] == 1
    assert verdict.reasoning_timeline[0]["agent_name"] == "CoordinatorAgent"
