from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings


class ChromaMemoryStore:
    """Isolates ChromaDB operations from the rest of the application."""

    def __init__(
        self,
        collection_name: str = "investigation_episodes",
        persist_directory: Optional[str] = None,
    ):
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            # Ephemeral client for tests or stateless execution
            self.client = chromadb.Client(Settings(allow_reset=True))

        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def insert(
        self,
        episode_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        text: str = "",
    ) -> None:
        """Inserts a single embedding with its associated metadata."""
        self.collection.upsert(
            ids=[episode_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text],
        )

    def delete(self, episode_id: str) -> None:
        """Deletes a vector record by ID."""
        self.collection.delete(ids=[episode_id])

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        metadata_filter: Dict[str, Any] = None,
    ) -> tuple[List[str], List[float]]:
        """
        Searches for the most similar episodes.
        Returns a tuple of (list of episode_ids, list of similarity scores/distances).
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=metadata_filter,
            include=["metadatas", "distances"],
        )

        if not results["ids"] or not results["ids"][0]:
            return [], []

        ids = results["ids"][0]
        distances = (
            results["distances"][0]
            if "distances" in results and results["distances"]
            else [0.0] * len(ids)
        )

        # Convert distances to a pseudo-similarity score where closer to 1 is better
        # For cosine distance, similarity = 1 - distance
        similarities = [1.0 - d for d in distances]

        return ids, similarities
