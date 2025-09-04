import logging
from fastapi import HTTPException
from sqlalchemy import desc, select
from app.db.session import SessionLocal
from app.services.embedder import get_embedder
from app.db.models import Chunk
import numpy as np

logger = logging.getLogger(__name__)

CONF_THRESHOLD = 0.35

async def run_search(q: str, k: int = 5):
    try:
        logger.info("Search called: q=%s k=%d", q, k)

        embedder = get_embedder()

        vec = await embedder.embed([q])
        logger.debug("Embedder returned %d vectors", len(vec) if hasattr(vec, "__len__") else 1)
        qvec = vec[0]
        logger.debug(
            "Query vector length/type: %s/%s",
            (len(qvec) if hasattr(qvec, "__len__") else "scalar"),
            type(qvec),
        )

        if isinstance(qvec, np.ndarray):
            qvec = qvec.tolist()

        stmt = (
            select(
                Chunk.id,
                Chunk.document_id,
                Chunk.text,
                (Chunk.embedding.cosine_distance(qvec)).label("score"),
            )
            .order_by("score")
            .limit(k)
        )

        # Execute the query
        logger.debug("Executing DB search for top-k=%d", k)
        results = []
        with SessionLocal() as db:
            results = db.execute(stmt).mappings().all()
        rows = [
                {
                    "chunk_id": str(result["id"]),
                    "document_id": str(result["document_id"]),
                    "text": result["text"],
                    "score": float(result["score"]),
                }
                for result in results
            ]

        response = {
            "query": q,
            "results": rows,
        }
        
        complete = False
        top_score = 0
        if not rows:
            complete = False
        else:
            top_score = rows[0]["score"]
            complete = top_score <= CONF_THRESHOLD
        response["top_score"] = top_score
        response["complete"] = complete
        logger.info("Search returned %d results for query", len(results))

        return response
    except Exception as e:
        logger.exception("Search failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")