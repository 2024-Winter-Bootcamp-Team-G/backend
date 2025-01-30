from fastapi import APIRouter
from celery.result import AsyncResult

router = APIRouter()


@router.get("/task/{task_id}/")
def get_task_status(task_id: str):
    """
    Celery Task 상태 조회 API
    """
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else "작업 진행 중",
    }