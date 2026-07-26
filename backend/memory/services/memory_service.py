import logging
from typing import Dict, List, Optional

from backend.memory.models.domain import (
    InvestigationEpisode,
    MemorySearchResult,
    SellerProfile,
)
from backend.memory.repositories.interfaces import (
    InvestigationRepository,
    SellerRepository,
)
from backend.memory.services.embedding_service import EmbeddingService
from backend.memory.vector.chroma_store import ChromaMemoryStore

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Orchestrator for the Long-Term Investigation Memory.
    Bridges SQLite (relational) and ChromaDB (vector) storage.
    """

    def __init__(
        self,
        investigation_repo: InvestigationRepository,
        seller_repo: SellerRepository,
        embedding_service: EmbeddingService,
        vector_store: ChromaMemoryStore,
    ):
        self.investigation_repo = investigation_repo
        self.seller_repo = seller_repo
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def save_episode(self, episode: InvestigationEpisode) -> None:
        """Saves an investigation episode to relational storage and vector memory."""
        logger.info(f"Saving InvestigationEpisode {episode.id}")

        # 1. Save Relational Data
        self.investigation_repo.save(episode)

        # 2. Update Seller Profile
        profile = self.seller_repo.get_by_identity(episode.seller_identity.name)
        if not profile:
            profile = SellerProfile(identity=episode.seller_identity)
        if episode.id not in profile.previous_episode_ids:
            profile.previous_episode_ids.append(episode.id)

        # Re-calculate overall trust score mock (placeholder logic)
        profile.overall_trust_score = (
            profile.overall_trust_score * 0.9 + episode.risk_score * 0.1
        )
        self.seller_repo.save(profile)

        # 3. Save Vector Data
        # Generate summary text for embedding
        embedding_text = self.generate_summary_text(episode)
        embedding = self.embedding_service.embed_text(embedding_text)

        metadata = {
            "seller_name": episode.seller_identity.name,
            "marketplace": episode.marketplace or "unknown",
            "risk_score": episode.risk_score,
            "verdict": episode.verdict,
        }

        self.vector_store.insert(
            episode_id=episode.id,
            embedding=embedding,
            metadata=metadata,
            text=embedding_text,
        )

    def get_episode(self, episode_id: str) -> Optional[InvestigationEpisode]:
        return self.investigation_repo.get_by_id(episode_id)

    def list_recent(self, limit: int = 10) -> List[InvestigationEpisode]:
        return self.investigation_repo.list_recent(limit)

    def search_similar(
        self,
        query_text: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
        metadata_filter: Optional[Dict] = None,
    ) -> List[MemorySearchResult]:
        """Searches vector memory for similar past investigations."""
        logger.info(f"Searching similar memories for query: '{query_text[:50]}...'")

        query_embedding = self.embedding_service.embed_text(query_text)
        ids, scores = self.vector_store.search(
            query_embedding, top_k=top_k, metadata_filter=metadata_filter
        )

        results = []
        for episode_id, score in zip(ids, scores):
            if score >= min_similarity:
                episode = self.investigation_repo.get_by_id(episode_id)
                if episode:
                    results.append(
                        MemorySearchResult(episode=episode, similarity_score=score)
                    )

        # Sort by highest score first
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results

    def generate_summary_text(self, episode: InvestigationEpisode) -> str:
        """Formats the episode into a string optimized for semantic embedding."""
        return (
            f"Seller: {episode.seller_identity.name}. "
            f"Marketplace: {episode.marketplace}. "
            f"Verdict: {episode.verdict}. "
            f"Risk Score: {episode.risk_score}. "
            f"Summary: {episode.summary}"
        )
