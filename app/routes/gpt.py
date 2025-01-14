from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.gpt_service import process_and_store_video_data
from app.db import get_db

router = APIRouter(prefix="/gpt", tags=["GPT"])


@router.post("/process/")
def process_video_data(redis_key: str, board_id: int, db: Session = Depends(get_db)):
    """
    Redis에서 raw data를 가져와 GPT로 분류 후 DB에 저장하는 API
    """
    try:
        result = process_and_store_video_data(db, redis_key, board_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
