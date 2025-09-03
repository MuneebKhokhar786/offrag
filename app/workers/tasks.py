# app/workers/tasks.py

import logging
logger = logging.getLogger(__name__)
from celery import shared_task
from app.services.embedder import MockEmbedder

embedder = MockEmbedder()

@shared_task
def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings asynchronously."""
    logger.info("generate_embeddings task started: %d texts", len(texts))
    try:
        result = embedder.embed(texts)
        logger.info("generate_embeddings task completed")
        return result
    except Exception as e:
        logger.error("generate_embeddings task failed: %s", e)
        raise
