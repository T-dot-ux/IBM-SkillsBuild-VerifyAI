from celery import Celery
from utils.config import settings

# Celery instance for async processing
celery_app = Celery(
    "verifyai_tasks",
    broker=settings.CELERY_BROKER_URL or "redis://localhost:6379/0",
    backend=settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Example task registration
# @celery_app.task(bind=True)
# def process_document_task(self, job_id: str, file_path: str):
#     # In production, this task would import process_verification_task from api.verify
#     pass
