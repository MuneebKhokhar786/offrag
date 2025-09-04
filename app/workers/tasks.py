import asyncio
import logging

from fastapi import Depends
from sqlalchemy import select

from app.db.models import Chunk
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)
from celery import shared_task
from app.services.embedder import get_embedder
from sqlalchemy.orm import Session
from app.db.session import get_db

embedder = get_embedder()


@shared_task
def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings asynchronously."""
    logger.info("generate_embeddings task started: %d texts", len(texts))
    try:
        vectors = asyncio.get_event_loop().run_until_complete(embedder.embed(texts))
        logger.info("generate_embeddings task completed")
        return vectors
    except Exception:
        logger.exception("generate_embeddings task failed")
        raise


@shared_task
def embed_pending_chunks(batch_size: int = 64, doc_id: str | None = None, db: Session = Depends(get_db) ):
    """Find chunks with embedding IS NULL (optionally for a document), embed them, save back.

    This task opens its own DB session so it can be run in a worker process.
    """
    db = SessionLocal()
    try:
        stmt = select(Chunk).where(Chunk.embedding == None)
        if doc_id:
            stmt = stmt.where(Chunk.document_id == doc_id)
        stmt = stmt.limit(batch_size)
        chunks = db.scalars(stmt).all()
        if not chunks:
            logger.info("embed_pending_chunks: no chunks pending")
            return "no chunks pending"
        texts = [c.text for c in chunks]
        vectors = asyncio.get_event_loop().run_until_complete(embedder.embed(texts))
        for c, vec in zip(chunks, vectors):
            c.embedding = vec
        db.commit()
        logger.info("embed_pending_chunks: embedded %d chunks", len(chunks))
        return f"embedded {len(chunks)} chunks"
    finally:
        db.close()