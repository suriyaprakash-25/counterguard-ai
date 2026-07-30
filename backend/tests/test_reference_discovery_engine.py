from typing import List

from backend.providers.discovery.base_provider import SearchProvider
from backend.providers.discovery.static_brand_provider import StaticBrandProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.services.discovery_pipeline import DiscoveryPipeline
from backend.services.reference_discovery_service import ReferenceDiscoveryService
from backend.services.source_deduplication_engine import SourceDeduplicationEngine
from backend.services.source_ranking_engine import SourceRankingEngine
from backend.services.source_verification_engine import SourceVerificationEngine


class FailingTestProvider(SearchProvider):
    """Failing test provider to verify pipeline error handling resilience."""

    @property
    def provider_name(self) -> str:
        return "FailingTestProvider"

    def search(self, query: str, brand: str = "") -> List[SourceCandidate]:
        raise RuntimeError("Simulated provider network failure")

    def supports(self, brand: str, domain: str = "") -> bool:
        return True

    def health_check(self) -> bool:
        return True


def test_source_candidate_extended_fields():
    candidate = SourceCandidate(
        title="Apple AirPods Pro",
        url="https://www.apple.com/airpods-pro/",
        provider="GoogleCSE",
        source_type="Official Store",
        confidence=0.95,
        retrieval_method="serp_api",
        response_time_ms=145.2,
        http_status=200,
        crawl_depth=1,
        language="en",
        region="US",
    )

    assert candidate.domain == "apple.com"
    assert candidate.retrieval_method == "serp_api"
    assert candidate.response_time_ms == 145.2
    assert candidate.http_status == 200
    assert candidate.timestamp is not None


def test_source_deduplication_engine():
    deduper = SourceDeduplicationEngine()

    c1 = SourceCandidate(
        title="Google Apple AirPods Result",
        url="https://apple.com/airpods",
        provider="GoogleCSE",
        source_type="Official Store",
        confidence=0.85,
    )
    c2 = SourceCandidate(
        title="SerpAPI Apple AirPods Result",
        url="https://www.apple.com/airpods/",
        provider="SerpAPI",
        source_type="Official Store",
        confidence=0.92,
    )

    deduped = deduper.deduplicate([c1, c2])
    # Should merge both URLs into ONE canonical candidate
    assert len(deduped) == 1
    assert "apple.com/airpods" in deduped[0].url
    assert deduped[0].confidence == 0.92  # Preserved highest confidence entry


def test_static_brand_provider_supported_brand():
    provider = StaticBrandProvider()
    assert provider.supports("nothing") is True
    assert provider.supports("nike") is True
    assert provider.supports("unknown_brand_xyz") is False

    results = provider.search(query="CMF Buds", brand="Nothing")
    assert len(results) == 1
    candidate = results[0]
    assert candidate.provider == "StaticBrandProvider"
    assert candidate.domain == "nothing.tech"
    assert candidate.source_type == "Official Store"
    assert candidate.confidence == 0.98


def test_static_brand_provider_unknown_brand():
    provider = StaticBrandProvider()
    results = provider.search(query="Unknown Product", brand="Unknown Brand XYZ")
    assert len(results) == 0


def test_source_ranking_engine():
    ranker = SourceRankingEngine()

    c1 = SourceCandidate(
        title="Marketplace Listing",
        url="https://amazon.com/item1",
        source_type="Marketplace",
        provider="TestProv",
        confidence=0.5,
    )
    c2 = SourceCandidate(
        title="Official Brand Store",
        url="https://nike.com/shoes",
        source_type="Official Store",
        provider="TestProv",
        confidence=0.98,
    )

    ranked = ranker.rank([c1, c2])
    assert len(ranked) == 2
    assert ranked[0].source_type == "Official Store"
    assert ranked[0].domain == "nike.com"
    assert ranked[1].source_type == "Marketplace"


def test_source_verification_engine():
    verifier = SourceVerificationEngine()

    cand_valid = SourceCandidate(
        title="Nothing Official Store",
        url="https://nothing.tech/products/buds",
        source_type="Official Store",
        provider="StaticBrandProvider",
        confidence=0.98,
    )

    cand_http = SourceCandidate(
        title="Insecure Store",
        url="http://nothing.tech/products/buds",
        source_type="Official Store",
        provider="StaticBrandProvider",
        confidence=0.98,
    )

    cand_bad_domain = SourceCandidate(
        title="Fake Store",
        url="https://scam-store-fake.xyz/item",
        source_type="Official Store",
        provider="StaticBrandProvider",
        confidence=0.98,
    )

    v1, r1 = verifier.verify_source(cand_valid, brand="nothing")
    assert v1 is True
    assert "Verified" in r1

    v2, r2 = verifier.verify_source(cand_http, brand="nothing")
    assert v2 is False
    assert "Non-HTTPS" in r2

    v3, r3 = verifier.verify_source(cand_bad_domain, brand="nothing")
    assert v3 is False
    assert "Domain not in allowed brand registry" in r3


def test_discovery_pipeline_end_to_end():
    pipeline = DiscoveryPipeline()
    res = pipeline.run(query="Air Force 1", brand="Nike")

    assert res.status == "success"
    assert len(res.candidate_sources) >= 1
    assert res.verified_source is not None
    assert res.verified_source.domain == "nike.com"
    assert res.confidence == 0.98
    assert "StaticBrandProvider" in res.providers_used
    assert res.metadata["deduped_candidate_count"] >= 1


def test_discovery_pipeline_provider_resilience():
    pipeline = DiscoveryPipeline(
        providers=[FailingTestProvider(), StaticBrandProvider()]
    )
    res = pipeline.run(query="Galaxy S24", brand="Samsung")

    assert res.status == "success"
    assert res.verified_source is not None
    assert res.verified_source.domain == "samsung.com"


def test_reference_discovery_service_end_to_end():
    service = ReferenceDiscoveryService()
    discovery_result, profile = service.discover(
        product_name="AirPods Pro", brand="Apple"
    )

    assert discovery_result.status == "success"
    assert discovery_result.verified_source is not None
    assert discovery_result.verified_source.domain == "apple.com"

    assert profile.brand == "Apple"
    assert profile.product_name == "AirPods Pro"
    assert profile.official_url == discovery_result.verified_source.url
    assert profile.confidence == 0.98
