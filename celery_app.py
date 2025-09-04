# celery_app.py
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

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
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=30,
    task_soft_time_limit=20,
    broker_transport_options={"visibility_timeout": 3600},
)

celery_app.autodiscover_tasks(["app.workers.tasks"])