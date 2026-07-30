from backend.collaboration.models.context import InvestigationContext
from backend.memory.models.domain import Evidence
from backend.services.verdict_engine import VerdictEngine


def test_evidence_driven_verdict_engine_outputs():
    ctx = InvestigationContext(investigation_id="inv_verdict_test")

    # Add 7 dimension evidence items
    ctx.add_evidence(
        Evidence(
            agent_name="PriceAgent",
            category="Price",
            title="Severe MSRP Drop",
            description="87% below MSRP",
            severity="critical",
            confidence=0.95,
        )
    )
    ctx.add_evidence(
        Evidence(
            agent_name="SellerAgent",
            category="Seller",
            title="Domain Age Audit",
            description="Seller created recently",
            severity="high",
            confidence=0.88,
        )
    )
    ctx.add_evidence(
        Evidence(
            agent_name="BrandIntelligenceAgent",
            category="Brand",
            title="Brand Verification",
            description="Missing manufacturer branding metadata",
            severity="high",
            confidence=0.85,
        )
    )
    ctx.add_evidence(
        Evidence(
            agent_name="ReviewAgent",
            category="Review",
            title="Visual Image Forensics",
            description="Duplicate listing images detected",
            severity="medium",
            confidence=0.90,
        )
    )
    ctx.add_evidence(
        Evidence(
            agent_name="TrustedProductAgent",
            category="Memory",
            title="Historical Case Search",
            description="Similar to previous counterfeit case",
            severity="high",
            confidence=0.92,
        )
    )

    verdict = VerdictEngine.evaluate_risk(
        raw_risk_score=82,
        product_name="Sony WH-1000XM5 Wireless Headphones",
        marketplace="Amazon",
        seller_name="Unverified Tech Deals",
        price=49.99,
        market_avg_price=399.99,
        context=ctx,
    )

    # 1. Core Verdict Classifications
    assert verdict.final_verdict in ["SUSPICIOUS", "LIKELY_COUNTERFEIT"]
    assert verdict.risk_score >= 70
    assert verdict.risk_level in ["HIGH", "CRITICAL"]

    # 2. Evidence-Driven Reasoning Fields
    assert hasattr(verdict, "overall_confidence")
    assert hasattr(verdict, "overall_reasoning")
    assert hasattr(verdict, "supporting_evidence")
    assert hasattr(verdict, "conflicting_evidence")

    assert verdict.overall_confidence > 0.50
    assert len(verdict.overall_reasoning) >= 3
    assert len(verdict.supporting_evidence) >= 3

    # Check bullet reasoning items
    reasoning_text = "\n".join(verdict.overall_reasoning)
    assert "87% below MSRP" in reasoning_text or "below MSRP" in reasoning_text
    assert (
        "Seller created recently" in reasoning_text
        or "Missing manufacturer" in reasoning_text
        or "Duplicate" in reasoning_text
    )


def test_evidence_driven_verdict_engine_conflicting_evidence():
    ctx = InvestigationContext(investigation_id="inv_conflict_test")

    # High risk price vs Low risk verified brand catalog
    ctx.add_evidence(
        Evidence(
            agent_name="PriceAgent",
            category="Price",
            title="Severe Discount",
            description="Price 80% below MSRP",
            severity="critical",
            confidence=0.9,
        )
    )
    ctx.add_evidence(
        Evidence(
            agent_name="BrandAgent",
            category="Brand",
            title="Official Catalog Match",
            description="Brand catalog verified authentic",
            severity="info",
            confidence=0.95,
        )
    )

    verdict = VerdictEngine.evaluate_risk(
        raw_risk_score=65,
        product_name="Nothing Phone (2a)",
        marketplace="Flipkart",
        seller_name="Authorized Retailer",
        price=199.99,
        context=ctx,
    )

    assert len(verdict.supporting_evidence) > 0
    assert len(verdict.conflicting_evidence) > 0
    assert (
        "Conflicting agent evidence detected" in verdict.reasoning
        or verdict.overall_confidence < 0.98
    )
