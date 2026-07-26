from typing import List

import pytest

from backend.memory.models.domain import (
    InvestigationEpisode,
    SellerIdentity,
    SellerProfile,
)
from backend.memory.repositories.sqlite_repository import (
    SQLiteInvestigationRepository,
    SQLiteSellerRepository,
)
from backend.memory.services.embedding_service import (
    EmbeddingProvider,
    EmbeddingService,
)
from backend.memory.services.memory_service import MemoryService
from backend.memory.vector.chroma_store import ChromaMemoryStore


class MockEmbeddingProvider(EmbeddingProvider):
    def generate_embedding(self, text: str) -> List[float]:
        # Simple deterministic mock embedding based on length
        return [float(len(text))] * 10


@pytest.fixture
def investigation_repo():
    return SQLiteInvestigationRepository(db_path=":memory:")


@pytest.fixture
def seller_repo():
    return SQLiteSellerRepository(db_path=":memory:")


@pytest.fixture
def embedding_service():
    return EmbeddingService(MockEmbeddingProvider())


@pytest.fixture
def vector_store():
    return ChromaMemoryStore(collection_name="test_episodes")


@pytest.fixture
def memory_service(investigation_repo, seller_repo, embedding_service, vector_store):
    return MemoryService(
        investigation_repo, seller_repo, embedding_service, vector_store
    )


def test_investigation_repository_crud(investigation_repo):
    episode = InvestigationEpisode(
        id="ep-123",
        seller_identity=SellerIdentity(name="BadSeller"),
        marketplace="Amazon",
        verdict="Counterfeit",
        risk_score=95.0,
        summary="Clear evidence of IP infringement.",
    )

    # Save
    investigation_repo.save(episode)

    # Get
    retrieved = investigation_repo.get_by_id("ep-123")
    assert retrieved is not None
    assert retrieved.seller_identity.name == "BadSeller"
    assert retrieved.risk_score == 95.0

    # List
    recent = investigation_repo.list_recent()
    assert len(recent) == 1

    # Delete
    investigation_repo.delete("ep-123")
    assert investigation_repo.get_by_id("ep-123") is None


def test_seller_repository_crud(seller_repo):
    profile = SellerProfile(
        identity=SellerIdentity(name="BadSeller", domain="badseller.com"),
        overall_trust_score=20.0,
        previous_episode_ids=["ep-1"],
    )

    seller_repo.save(profile)

    retrieved = seller_repo.get_by_identity("BadSeller")
    assert retrieved is not None
    assert retrieved.overall_trust_score == 20.0
    assert "ep-1" in retrieved.previous_episode_ids


def test_memory_service_orchestration(memory_service, seller_repo):
    episode = InvestigationEpisode(
        id="ep-999",
        seller_identity=SellerIdentity(name="OrchestrationSeller"),
        marketplace="eBay",
        verdict="Authentic",
        risk_score=10.0,
        summary="All checks passed.",
    )

    # 1. Save Episode (Should hit SQLite Repos and Chroma)
    memory_service.save_episode(episode)

    # Verify Seller Profile updated
    profile = seller_repo.get_by_identity("OrchestrationSeller")
    assert profile is not None
    assert "ep-999" in profile.previous_episode_ids

    # Verify Search
    query = "Brand: Nike. Title: Shoes. Seller: OrchestrationSeller"
    results = memory_service.search_similar(query, top_k=1, min_similarity=0.0)

    assert len(results) == 1
    assert results[0].episode.id == "ep-999"
