from backend.agents.assessor import RiskAssessor
from backend.agents.coordinator import CoordinatorAgent
from backend.agents.intelligence_agents import SpecificationValidationAgent
from backend.agents.specialists import BrandAgent, PriceAgent
from backend.agents.visual import VisualForensicsAgent
from backend.schemas.canonical_product import CanonicalProductKnowledge
from backend.schemas.intelligence import SpecificationValidationResult
from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationRequest,
)
from backend.schemas.llm_models import PriceAnalysisResult
from backend.services.investigation_service import InvestigationService
from backend.state import InvestigationState


def test_price_agent_canonical_msrp_comparison():
    agent = PriceAgent()
    cpk = CanonicalProductKnowledge(
        brand="Apple",
        product_name="AirPods Pro (2nd Gen)",
        canonical_id="apple-airpods-pro-2nd-gen",
        msrp=24900.0,
        currency="INR",
    )

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
        "canonical_product_knowledge": cpk,
    }

    mock_llm_res = PriceAnalysisResult(
        anomaly_detected=True, risk_score=50, reasoning="LLM Base"
    )
    updates = agent._update_state(state, mock_llm_res)

    context = updates["context"]
    ev = context.shared_evidence[0]
    assert ev.metadata["price_difference_percentage"] == 79.9
    assert ev.metadata["discount_classification"] == "extreme_discount"
    assert ev.metadata["canonical_msrp"] == 24900.0
    assert updates["price_analysis"].risk_score == 90


def test_specification_validation_agent_canonical_mismatch():
    agent = SpecificationValidationAgent()
    cpk = CanonicalProductKnowledge(
        brand="Samsung",
        product_name="Galaxy S24 Ultra",
        canonical_id="samsung-galaxy-s24-ultra",
        canonical_specs={"battery_capacity": "5000 mAh", "storage": "512 GB"},
    )

    state: InvestigationState = {
        "scraping_result": type(
            "MockScrapingResult",
            (),
            {
                "listing": type(
                    "MockListing",
                    (),
                    {
                        "title": "Samsung Galaxy S24 Ultra Fake Edition",
                        "description": "Awesome phone with 3000mAh battery and 64GB storage.",
                    },
                )()
            },
        )(),
        "canonical_product_knowledge": cpk,
    }

    mock_res = SpecificationValidationResult(
        risk_score=30, reasoning="Spec audit", missing_specs=[], inconsistent_specs=[]
    )

    updates = agent._update_state(state, mock_res)
    ev = updates["context"].shared_evidence[0]
    assert len(ev.metadata["inconsistent_specs"]) >= 1
    assert "Specification mismatch" in ev.metadata["inconsistent_specs"][0]


def test_brand_agent_canonical_mismatch():
    agent = BrandAgent()
    cpk = CanonicalProductKnowledge(
        brand="Nothing",
        product_name="CMF Buds",
        canonical_id="nothing-cmf-buds",
    )

    state: InvestigationState = {
        "scraping_result": type(
            "MockScrapingResult",
            (),
            {"listing": type("MockListing", (), {"brand": "Notting Store"})()},
        )(),
        "canonical_product_knowledge": cpk,
    }

    mock_res = type(
        "MockBrandRes", (), {"risk_score": 30, "reasoning": "Brand check"}
    )()
    updates = agent._update_state(state, mock_res)
    assert updates["brand_analysis"].risk_score == 85
    assert "Brand mismatch" in updates["brand_analysis"].reasoning


def test_visual_forensics_agent_canonical_verified_images():
    agent = VisualForensicsAgent()
    cpk = CanonicalProductKnowledge(
        brand="Sony",
        product_name="WH-1000XM5",
        canonical_id="sony-wh-1000xm5",
        verified_images=["https://sony.com/verified_xm5.jpg"],
    )

    state: InvestigationState = {
        "scraping_result": type(
            "MockScrapingResult",
            (),
            {
                "listing": type(
                    "MockListing",
                    (),
                    {"title": "Sony WH-1000XM5", "image_url": "https://fake.jpg"},
                )()
            },
        )(),
        "canonical_product_knowledge": cpk,
    }

    res = agent.run(state)
    assert "visual_similarity" in res
    assert isinstance(res["visual_similarity"], float)


def test_coordinator_agent_evidence_correlation():
    agent = CoordinatorAgent()
    cpk = CanonicalProductKnowledge(
        brand="Nike",
        product_name="Air Force 1 '07",
        canonical_id="nike-air-force-1-07",
        msrp=115.0,
    )

    from backend.collaboration.models.context import InvestigationContext

    mock_context = InvestigationContext(investigation_id="temp")

    state: InvestigationState = {
        "canonical_product_knowledge": cpk,
        "context": mock_context,
        "visual_findings": ["Visual Mismatch: Differing logo placement"],
    }

    res = agent.run(state)
    assert "coordinator_result" in res
    assert "explanation" in res
    assert "Canonical Knowledge Baseline" in res["explanation"]


def test_risk_assessor_weighted_evaluation():
    assessor = RiskAssessor()
    analysis = AnalyzerResult(
        brand="GenericBrand",
        title="Cheap Counterfeit Item",
        price=100.0,
        seller_rating=2.0,
        marketplace="GenericMarket",
        risk_signals=["Very low price"],
    )
    evidence = EvidenceResult(
        structured_evidence={
            "price": {"status": "Suspicious"},
            "seller": {"status": "Poor"},
            "warranty": {"status": "Missing"},
        }
    )

    risk_res = assessor.assess(analysis, evidence)
    assert risk_res.risk_score >= 60
    assert risk_res.risk_level in ("HIGH", "CRITICAL", "MEDIUM")


def test_e2e_investigation_service_across_brands():
    """Runs end-to-end investigation workflow across 6 major brand products."""
    service = InvestigationService()

    test_brands = [
        {
            "brand": "Nothing",
            "product": "Phone (2a)",
            "url": "https://nothing.tech/products/phone-2a",
        },
        {
            "brand": "Apple",
            "product": "AirPods Pro",
            "url": "https://apple.com/airpods-pro",
        },
        {
            "brand": "Samsung",
            "product": "Galaxy S24",
            "url": "https://samsung.com/galaxy-s24",
        },
        {"brand": "Sony", "product": "WH-1000XM5", "url": "https://sony.com/wh1000xm5"},
        {
            "brand": "Nike",
            "product": "Air Force 1",
            "url": "https://nike.com/shoes/af1",
        },
        {
            "brand": "Adidas",
            "product": "Samba OG",
            "url": "https://adidas.com/shoes/samba",
        },
    ]

    for item in test_brands:
        req = InvestigationRequest(
            listing_url=item["url"],
            marketplace="VerifiedMarket",
            target_value=item["product"],
        )
        report = service.run_investigation(req)
        assert report is not None
        assert report.risk_score >= 0
        assert report.risk_level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
