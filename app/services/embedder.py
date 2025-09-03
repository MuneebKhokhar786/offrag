import logging
logger = logging.getLogger(__name__)
from abc import ABC, abstractmethod
from typing import List

class BaseEmbedder(ABC):
    """Abstract interface for embedding providers."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return embeddings for given texts."""
        pass


class MockEmbedder(BaseEmbedder):
    """Mock embedder for local dev/testing."""

    def embed(self, texts: List[str]) -> List[List[float]]:
        logger.debug("MockEmbedder.embed called with %d texts", len(texts))
        embeddings = [[float(len(t))] * 5 for t in texts]
        logger.debug("MockEmbedder generated embeddings for first item: %s", embeddings[0] if embeddings else None)
        return embeddings