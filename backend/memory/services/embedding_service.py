from abc import ABC, abstractmethod
from typing import List

from openai import OpenAI

from backend.settings import settings


class EmbeddingProvider(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI implementation of EmbeddingProvider."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            # We provide a dummy key to prevent crashes in CI environments
            self.client = OpenAI(api_key="dummy")
        else:
            self.client = OpenAI(api_key=api_key)

    def generate_embedding(self, text: str) -> List[float]:
        """Generates an embedding for the given text using OpenAI."""
        if self.client.api_key == "dummy":
            # Mock embedding for test environments
            return [0.0] * 1536

        # Normalize text by replacing newlines
        normalized_text = text.replace("\n", " ")
        response = self.client.embeddings.create(
            input=[normalized_text], model=self.model
        )
        return response.data[0].embedding


class EmbeddingService:
    """Service for handling text embeddings via a configured provider."""

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def embed_text(self, text: str) -> List[float]:
        """Generates an embedding for the provided text."""
        return self.provider.generate_embedding(text)
