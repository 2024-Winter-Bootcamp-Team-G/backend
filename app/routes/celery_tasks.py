from fastapi import APIRouter
from app.services.celery_tasks import add
from app.utils.celery_app import celery_app

router = APIRouter(prefix="/tasks")


@router.get("/add/")
async def add_numbers(x: int, y: int):
    task = add.delay(x, y)  # Celery 작업 호출
    return {"task_id": task.id, "status": "Task submitted"}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {"task_id": task.id, "status": task.status}
