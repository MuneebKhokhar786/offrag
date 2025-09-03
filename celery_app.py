# celery_app.py
from celery import Celery

celery_app = Celery(
    "off_agents",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_routes={
        "app.workers.tasks.*": {"queue": "agents"},
    },
    task_default_retry_delay=5,
    task_annotations={
        "*": {"max_retries": 3, "time_limit": 30},
    },
)

