from backend.agents.specialists import SellerAgent
from backend.collaboration.models.context import InvestigationContext
from backend.memory.models.domain import Evidence
from backend.schemas.llm_models import SellerAnalysisResult
from backend.services.verdict_engine import VerdictEngine
from backend.state import merge_context


def test_evidence_model_instantiation():
    ev = Evidence(
        agent_name="PriceAgent",
        category="Price",
        title="Severe MSRP Drop",
        description="Product is listed at 90% below standard market price.",
        severity="critical",
        confidence=0.92,
        source="price_history",
    )

    assert ev.id is not None
    assert ev.agent_name == "PriceAgent"
    assert ev.source_agent == "PriceAgent"
    assert ev.category.upper() == "PRICE"
    assert ev.severity == "critical"
    assert ev.confidence == 0.92
    assert "90% below" in ev.description
    assert isinstance(ev.timestamp, str)


def test_investigation_context_evidence_operations():
    ctx = InvestigationContext(investigation_id="inv_test_101", marketplace="Amazon")

    ev1 = Evidence(
        agent_name="PriceAgent",
        category="Price",
        title="Price Anomaly",
        description="Listed price is ₹210 vs MSRP ₹2,499",
        severity="critical",
        confidence=0.95,
        source="price_history",
    )

    ev2 = Evidence(
        agent_name="SellerAgent",
        category="Seller",
        title="New Unverified Merchant",
        description="Seller domain created 10 days ago",
        severity="high",
        confidence=0.85,
        source="whois_lookup",
    )

    ctx.add_evidence(ev1)
    ctx.add_evidence(ev2)

    # Test evidence properties & execution order
    assert len(ctx.evidence) == 2
    assert ctx.evidence[0].agent_name == "PriceAgent"
    assert ctx.evidence[1].agent_name == "SellerAgent"

    # Filter by agent
    price_ev = ctx.get_evidence_by_agent("PriceAgent")
    assert len(price_ev) == 1
    assert price_ev[0].title == "Price Anomaly"

    # Filter by category
    seller_ev = ctx.get_evidence_by_category("Seller")
    assert len(seller_ev) == 1
    assert seller_ev[0].severity == "high"

    # Intermediate risk calculation test
    assert ctx.intermediate_risk > 0.0
    assert len(ctx.confidence_history) == 2


def test_merge_context_reducer_deduplication():
    ctx_a = InvestigationContext(investigation_id="inv_merge")
    ev1 = Evidence(
        evidence_id="ev_fixed_1",
        agent_name="PriceAgent",
        category="Price",
        title="Price Drop",
        description="Price is low",
        severity="high",
        confidence=0.8,
    )
    ctx_a.add_evidence(ev1)

    ctx_b = InvestigationContext(investigation_id="inv_merge")
    ev2 = Evidence(
        evidence_id="ev_fixed_2",
        agent_name="BrandAgent",
        category="Brand",
        title="Trademark Check",
        description="Unverified Brand",
        severity="medium",
        confidence=0.7,
    )
    # Re-adding ev1 to test deduplication
    ctx_b.add_evidence(ev1)
    ctx_b.add_evidence(ev2)

    merged = merge_context(ctx_a, ctx_b)

    assert len(merged.shared_evidence) == 2
    evidence_ids = [e.evidence_id for e in merged.shared_evidence]
    assert "ev_fixed_1" in evidence_ids
    assert "ev_fixed_2" in evidence_ids


def test_contextual_confidence_propagation_price_to_seller():
    ctx = InvestigationContext(investigation_id="inv_prop")
    # Step 1: PriceAgent adds severe price anomaly evidence
    price_ev = Evidence(
        agent_name="PriceAgent",
        category="Price",
        title="Severe MSRP Drop",
        description="Price 90% below market",
        severity="critical",
        confidence=0.95,
    )
    ctx.add_evidence(price_ev)

    # Step 2: SellerAgent executes and inspects state context
    seller_agent = SellerAgent()
    mock_state = {"context": ctx, "scraping_result": None, "request": None}

    # Seller initial analysis result
    mock_seller_res = SellerAnalysisResult(
        reputation_risk="High", reasoning="Domain age 14 days", risk_score=50
    )

    updates = seller_agent._update_state(mock_state, mock_seller_res)
    updated_seller_res = updates["seller_analysis"]

    # Verify suspicion risk score was elevated from 50 to 57 (+15%)
    assert updated_seller_res.risk_score > 50
    assert "Suspicion elevated" in updated_seller_res.reasoning


def test_coordinator_verdict_engine_conflict_detection():
    ctx = InvestigationContext(investigation_id="inv_conflicts")

    # Conflicting Evidence: High price risk vs Low brand risk
    ctx.add_evidence(
        Evidence(
            agent_name="PriceAgent",
            category="Price",
            title="Critical Discount",
            description="Price 85% off",
            severity="critical",
            confidence=0.9,
        )
    )
    ctx.add_evidence(
        Evidence(
            agent_name="BrandAgent",
            category="Brand",
            title="Verified Catalog Match",
            description="Product matched official catalog",
            severity="info",
            confidence=0.95,
        )
    )

    verdict = VerdictEngine.evaluate_risk(
        raw_risk_score=75,
        product_name="Nothing Phone (2a)",
        marketplace="Amazon",
        seller_name="Verified Outlet",
        price=199.99,
        context=ctx,
    )

    assert verdict.final_verdict in ["SUSPICIOUS", "LIKELY_COUNTERFEIT"]
    assert "Conflicting agent evidence detected" in verdict.reasoning
    assert verdict.confidence <= 0.95
