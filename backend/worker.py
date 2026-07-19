from celery import Celery
import os

# Initialize Celery app
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "verify_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["api.verify"] 
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
