from fastapi import APIRouter, Query
from app.orchestrator import Orchestrator

router = APIRouter()

@router.get("/orchestrate")
async def orchestrate(q: str = Query(..., description="User query")):
    orch = Orchestrator()
    result = await orch.handle(q)
    return result