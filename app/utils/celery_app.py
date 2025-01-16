from app.config import settings
from celery import Celery

app = Celery("backend", broker=settings.CELERY_BROKER_URL)
app.conf.broker_connection_retry_on_startup = (
    settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP
)

celery_app = Celery(
    "backend",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
)

celery_app.conf.task_routes = {
    "app.services.celery_tasks.add": {"queue": "default"},
    "app.services.celery_tasks.send_email": {"queue": "email"},
}
