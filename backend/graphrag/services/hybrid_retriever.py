import logging
from typing import Any, Dict

from backend.graph.repositories.interfaces import GraphRepository
from backend.memory.repositories.interfaces import (
    InvestigationRepository,
    SellerRepository,
)
from backend.memory.services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Orchestrates queries across SQLite, ChromaDB, and Neo4j.
    Merges results, removes duplicates, and normalizes entities.
    """

    def __init__(
        self,
        investigation_repo: InvestigationRepository,
        seller_repo: SellerRepository,
        memory_service: MemoryService,
        graph_repo: GraphRepository,
    ):
        self.investigation_repo = investigation_repo
        self.seller_repo = seller_repo
        self.memory_service = memory_service
        self.graph_repo = graph_repo

    def retrieve(self, seller_name: str, listing_title: str) -> Dict[str, Any]:
        """Retrieves and normalizes data from all sources."""
        logger.info(f"Running hybrid retrieval for seller: {seller_name}")

        # 1. Semantic Search (ChromaDB)
        query = f"Seller: {seller_name}. Title: {listing_title}"
        semantic_memories = self.memory_service.search_similar(
            query, top_k=5, min_similarity=0.4
        )

        # 2. Exact Match (SQLite)
        seller_profile = self.seller_repo.get_by_identity(name=seller_name)
        past_investigations = []
        if seller_profile:
            for ep_id in seller_profile.previous_episode_ids:
                ep = self.investigation_repo.get_by_id(ep_id)
                if ep:
                    past_investigations.append(ep)

        # 3. Graph Retrieval (Neo4j)
        graph_nodes = []
        try:
            seller_node = self.graph_repo.get_node(seller_name, "Seller")
            if seller_node:
                # Naive retrieval of 1st-degree connections using run_query
                cypher = """
                MATCH (s:Seller {id: $name})-[r]-(connected)
                RETURN type(r) as rel_type, connected.id as target, labels(connected)[0] as label
                """
                graph_nodes = self.graph_repo.run_query(cypher, {"name": seller_name})
        except Exception as e:
            logger.warning(f"Graph retrieval failed (mock/unconnected): {e}")

        # 4. Merge & Deduplicate
        seen_episodes = set()
        merged_episodes = []

        # Add semantic
        for m in semantic_memories:
            if m.episode.id not in seen_episodes:
                seen_episodes.add(m.episode.id)
                merged_episodes.append(
                    {
                        "episode": m.episode,
                        "source": "semantic",
                        "similarity": m.similarity_score,
                    }
                )

        # Add exact
        for ep in past_investigations:
            if ep.id not in seen_episodes:
                seen_episodes.add(ep.id)
                merged_episodes.append(
                    {
                        "episode": ep,
                        "source": "exact",
                        "similarity": 1.0,  # Exact match
                    }
                )

        return {
            "seller_profile": seller_profile.model_dump() if seller_profile else None,
            "merged_episodes": merged_episodes,
            "graph_connections": graph_nodes,
        }
