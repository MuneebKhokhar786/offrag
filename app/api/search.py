import asyncio
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, select, func
from app.db.session import get_db
from app.services.embedder import get_embedder
from app.db.models import Chunk
import numpy as np

router = APIRouter()
logger = logging.getLogger(__name__)

CONF_THRESHOLD = 0.6

@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    k: int = Query(5, ge=1, le=20, description="Top-K results"),
    with_check: bool = Query(False, description="Whether to perform completeness check"),
    db: Session = Depends(get_db),
):
    try:
        logger.info("Search called: q=%s k=%d", q, k)

        # Get the embedder and generate the query vector (support sync and async embedders)
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
            .order_by(desc("score"))
            .limit(k)
        )

        # Execute the query
        logger.debug("Executing DB search for top-k=%d", k)
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
        top_score = None
        if with_check:
            if not rows:
                complete = False
            else:
                top_score = rows[0]["score"]
                response["top_score"] = top_score
                complete = top_score <= CONF_THRESHOLD
            response["complete"] = complete
            logger.info("Search returned %d results for query", len(results))

        return response
    except Exception as e:
        logger.exception("Search failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")