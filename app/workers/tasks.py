# app/workers/tasks.py
from celery import shared_task
from app.services.embedder import MockEmbedder

embedder = MockEmbedder()

@shared_task
def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings asynchronously."""
    return embedder.embed(texts)
