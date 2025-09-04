import logging
from fastapi import APIRouter, Query
from app.services.search_service import run_search

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    k: int = Query(5, ge=1, le=20, description="Top-K results"),
    with_check: bool = Query(False, description="Whether to perform completeness check")
):
    result = await run_search(q, k)
    if not with_check:
        result.pop("complete", None)
    return {"query": q, **result}