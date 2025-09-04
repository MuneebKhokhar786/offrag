import logging
import os
from random import random
from abc import ABC, abstractmethod
from httpx import AsyncClient
from typing import List

logger = logging.getLogger(__name__)
class BaseEmbedder(ABC):
    """Abstract interface for embedding providers."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return embeddings for given texts."""
        pass


class MockEmbedder(BaseEmbedder):
    """Generates random vectors for local testing."""
    def __init__(self, dim: int = 1536):
        self.dim = dim
    async def embed(self, texts: List[str]) -> List[List[float]]:
        return [[random() for _ in range(self.dim)] for _ in texts]
    
class OpenAIEmbedder(BaseEmbedder):
    """Call OpenAI embeddings API."""
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.openai.com/v1/embeddings"

    async def embed(self, texts: List[str]) -> List[List[float]]:
        async with AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": texts, "model": self.model}
            )
            resp.raise_for_status()
            data = resp.json()
            return [d["embedding"] for d in data["data"]]
        
def get_embedder() -> BaseEmbedder:
    """Factory that selects embedder from env."""
    provider = os.getenv("EMBEDDING_PROVIDER", "mock")
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        return OpenAIEmbedder(key)
    return MockEmbedder()