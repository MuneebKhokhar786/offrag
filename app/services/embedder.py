import logging
import os
from random import random
from abc import ABC, abstractmethod
from httpx import AsyncClient
from typing import List

from sentence_transformers import SentenceTransformer
import torch

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
        
class SentenceTransformerEmbedder:
    """Minimal embedder using sentence-transformers/all-MiniLM-L6-v2 model."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = None):
        """
        Initialize the sentence transformer embedder.
        
        Args:
            model_name: Name of the sentence transformer model
            device: Device to run the model on ('cpu', 'cuda', etc.). 
                   If None, uses GPU if available, otherwise CPU.
        """
        self.model = SentenceTransformer(model_name, device=device)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of strings to embed
            
        Returns:
            List of embedding vectors as lists of floats
        """
        if not texts:
            return []
        
        # Convert to numpy array and then to list of lists for consistency
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Make the instance callable for convenience."""
        return self.embed(texts)
        
def get_embedder() -> BaseEmbedder:
    """Factory that selects embedder from env."""
    provider = os.getenv("EMBEDDING_PROVIDER", "mock")
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        return OpenAIEmbedder(key)
    elif provider == "sentence-transformers":
        model_name = os.getenv("SENTENCE_TRANSFORMERS_MODEL", "all-MiniLM-L6-v2")
        return SentenceTransformerEmbedder(model_name, device="cuda" if torch.cuda.is_available() else "cpu")
    return MockEmbedder(384)