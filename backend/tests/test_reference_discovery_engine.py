from typing import List

from backend.providers.discovery.base_provider import SearchProvider
from backend.providers.discovery.static_brand_provider import StaticBrandProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.services.discovery_pipeline import DiscoveryPipeline
from backend.services.reference_discovery_service import ReferenceDiscoveryService
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


def test_static_brand_provider_supported_brand():
    provider = StaticBrandProvider()
    assert provider.supports("nothing") is True
    assert provider.supports("nike") is True
    assert provider.supports("unknown_brand_xyz") is False

    results = provider.search(query="CMF Buds", brand="Nothing")
    assert len(results) == 1
    candidate = results[0]
    assert candidate.provider == "StaticBrandProvider"
    assert "nothing.tech" in candidate.url
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
    c3 = SourceCandidate(
        title="Duplicate Official Brand Store",
        url="https://nike.com/shoes/",
        source_type="Official Store",
        provider="TestProv",
        confidence=0.98,
    )

    ranked = ranker.rank([c1, c2, c3])
    # Duplicate URL should be removed, and Official Store ranked first
    assert len(ranked) == 2
    assert ranked[0].source_type == "Official Store"
    assert "nike.com" in ranked[0].url
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
    assert "nike.com" in res.verified_source.url
    assert res.confidence == 0.98
    assert "StaticBrandProvider" in res.providers_used


def test_discovery_pipeline_provider_resilience():
    pipeline = DiscoveryPipeline(
        providers=[FailingTestProvider(), StaticBrandProvider()]
    )
    res = pipeline.run(query="Galaxy S24", brand="Samsung")

    # Should gracefully bypass FailingTestProvider and succeed via StaticBrandProvider
    assert res.status == "success"
    assert res.verified_source is not None
    assert "samsung.com" in res.verified_source.url


def test_reference_discovery_service_end_to_end():
    service = ReferenceDiscoveryService()
    discovery_result, profile = service.discover(
        product_name="AirPods Pro", brand="Apple"
    )

    assert discovery_result.status == "success"
    assert discovery_result.verified_source is not None
    assert "apple.com" in discovery_result.verified_source.url

    assert profile.brand == "Apple"
    assert profile.product_name == "AirPods Pro"
    assert profile.official_url == discovery_result.verified_source.url
    assert profile.confidence == 0.98
