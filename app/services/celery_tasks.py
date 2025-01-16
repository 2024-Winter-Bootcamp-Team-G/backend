from app.utils.celery_app import celery_app


@celery_app.task
def test_task():
    return "Task executed successfully!"


@celery_app.task
def add(x, y):
    return x + y
