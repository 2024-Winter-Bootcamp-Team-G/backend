from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.board import BoardCreate
from app.services.board_service import get_boards, get_board_by_id, create_board
from app.db import get_db

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.post("/", response_model=dict)
async def create_new_board(board_data: BoardCreate, db: Session = Depends(get_db)):
    """
    보드 생성:
    1. Redis에서 raw 데이터를 가져옴.
    2. GPT로 카테고리 및 키워드를 생성.
    3. 생성된 키워드/카테고리를 기반으로 이미지를 생성.
    4. 결과를 DB에 저장.
    """

    redis_key = "youtube_raw_data"  # Redis 키를 하드코딩 또는 환경 변수로 지정
    user_id = 1  # 임시 user_id

    try:
        result = await create_board(db, board_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보드 생성 중 오류 발생: {str(e)}",
        )


# 보드 목록 조회
@router.get("/", response_model=dict)
def read_boards(db: Session = Depends(get_db)):
    boards = get_boards(db)
    return {
        "message": "보드 목록 조회에 성공했습니다.",
        "result": {
            "board": [
                {
                    "id": board.id,
                    "board_name": board.board_name,
                    "created_at": board.created_at,
                }
                for board in boards
            ]
        },
    }


# 보드 상세 조회
@router.get("/{board_id}", response_model=dict)
def read_board(board_id: int, db: Session = Depends(get_db)):
    board = get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return {
        "message": "요청한 보드 정보가 성공적으로 반환되었습니다.",
        "result": {
            "board": {
                "board_name": board.board_name,
                "image_url": board.image_url,
                "category_ratio": board.category_ratio,
                "keyword": board.keyword,
                "created_at": board.created_at,
            }
        },
    }


from fastapi import APIRouter, HTTPException
from app.utils.redis_handler import RedisHandler
import json


@router.get("/redis")
def test_redis_data(redis_key: str = "youtube_raw_data"):
    """
    Redis에서 데이터를 읽어오는 테스트 라우트
    """
    try:
        raw_data = RedisHandler.get_youtube_raw_data(redis_key)
        parsed_data = json.loads(raw_data)  # JSON 문자열을 Python dict로 변환
        return {"message": "Redis 데이터 읽기 성공", "data": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis 테스트 실패: {str(e)}")
