from app.config import settings
from celery import Celery

celery_app = Celery(
    "backend",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    broker_connection_retry_on_startup=settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.services.celery_tasks"])
celery_app.conf.task_routes = {
    "app.services.celery_tasks.create_board_task": {"queue": "default"},
}
