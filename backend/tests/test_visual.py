from backend.agents.visual import VisualForensicsAgent
from backend.schemas.investigation import InvestigationRequest
from backend.services.investigation_service import InvestigationService
from backend.services.scraping_service import ScrapingService


def test_visual_agent_genuine_high_similarity():
    """
    Test that demo://genuine's image against the golden reference scores high similarity (>75%),
    and produces zero visual mismatch findings.
    """
    agent = VisualForensicsAgent()
    scraping_service = ScrapingService(demo_mode=True)
    scraping_result = scraping_service.scrape("demo://genuine")

    state = {
        "request": InvestigationRequest(
            listing_url="demo://genuine",
            product_name="Sony WH-1000XM5 Wireless Headphones",
            marketplace="Sony Direct Store",
        ),
        "scraping_result": scraping_result,
    }

    res = agent.run(state)

    assert "visual_similarity" in res
    assert (
        res["visual_similarity"] >= 75.0
    ), f"Expected similarity >= 75%, got {res['visual_similarity']}%"
    assert (
        len(res["visual_findings"]) == 0
    ), f"Expected 0 visual mismatch findings, got {res['visual_findings']}"


def test_visual_agent_mismatch_produces_high_severity_finding():
    """
    Test that a visually different image scores low similarity (<75%) and produces
    a HIGH severity finding that escalates the final risk tier.
    """
    agent = VisualForensicsAgent()
    scraping_service = ScrapingService(demo_mode=True)
    scraping_result = scraping_service.scrape("demo://counterfeit")

    state = {
        "request": InvestigationRequest(
            listing_url="demo://counterfeit",
            product_name="Sony WH-1000XM5 Wireless Headphones",
            marketplace="Discount Replica Outlet",
        ),
        "scraping_result": scraping_result,
    }

    res = agent.run(state)

    assert "visual_similarity" in res
    assert (
        res["visual_similarity"] < 75.0
    ), f"Expected similarity < 75%, got {res['visual_similarity']}%"
    assert len(res["visual_findings"]) == 1
    assert "Visual Mismatch" in res["visual_findings"][0]


def test_visual_mismatch_escalates_risk_tier():
    """
    Test end-to-end pipeline execution for a visually mismatched product listing.
    Verifies that Visual Mismatch finding escalates risk_level to CRITICAL or LIKELY_COUNTERFEIT.
    """
    service = InvestigationService()
    req = InvestigationRequest(
        listing_url="demo://counterfeit",
        product_name="Sony WH-1000XM5 Wireless Headphones",
        marketplace="Discount Replica Outlet",
    )

    report = service.run_investigation(req)

    assert report.risk_level == "CRITICAL"
    assert report.risk_score >= 80
    assert any(
        "Visual Mismatch" in f or "Counterfeit Indicator" in f or "Replica" in f
        for f in report.findings
    )
