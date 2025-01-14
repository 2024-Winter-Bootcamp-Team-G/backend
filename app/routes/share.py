from fastapi import APIRouter, HTTPException
from app.utils.shared_link import create_shared_link
from app.utils.redis_handler import redis_client

router = APIRouter()

@router.post("/share")
async def share_board(board_id: int):
    shared_link = create_shared_link(board_id)
    return {"message": "보드 공유에 성공했습니다.", "result": {"shared_link": shared_link}}

@router.get("/shared-link/{board_id}")
def get_shared_link(board_id: int):
    shared_link = redis_client.get(f"shared_link:{board_id}")
    if not shared_link:
        raise HTTPException(
            status_code=404,
            detail={"message": "공유 링크가 만료되었거나 존재하지 않습니다."}
        )
    return {"message": "공유 링크 조회에 성공했습니다.", "result": {"shared_link": shared_link}}