
import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter
from celery.result import AsyncResult
from celery_app import celery_app
from app.workers.tasks import generate_embeddings

router = APIRouter()

@router.post("/embed/")
def create_embedding(texts: list[str]):
    logger.info("create_embedding called with %d texts", len(texts))
    task = generate_embeddings.apply_async(args=[texts], queue='agents')
    logger.info("Dispatched embedding task id=%s", task.id)
    return {"task_id": task.id}

@router.get("/result/{task_id}")
def get_result(task_id: str):
    logger.debug("get_result called for task_id=%s", task_id)
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        res = result.get()
        logger.info("Task %s completed", task_id)
        return {"status": "done", "result": res}
    logger.debug("Task %s not ready", task_id)
    return {"status": "pending"}
