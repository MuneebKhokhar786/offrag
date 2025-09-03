from fastapi import APIRouter
from celery.result import AsyncResult
from celery_app import celery_app
from app.workers.tasks import generate_embeddings

router = APIRouter()

@router.post("/embed/")
def create_embedding(texts: list[str]):
    task = generate_embeddings.delay(texts)
    return {"task_id": task.id}

@router.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return {"status": "done", "result": result.get()}
    return {"status": "pending"}
