from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.board import BoardCreate
from app.services.board_service import get_boards, get_board_by_id, create_board
from app.db import get_db

router = APIRouter(prefix="/boards", tags=["Boards"])


# 보드 생성
@router.post("/", response_model=dict)
async def create_new_board(board: BoardCreate, db: Session = Depends(get_db)):
    """
    보드 생성:
    1. Redis에서 raw 데이터를 가져옴.
    2. GPT로 카테고리 및 키워드를 생성.
    3. 생성된 키워드/카테고리를 기반으로 이미지를 생성.
    4. 결과를 DB에 저장.
    """
    try:
        new_board = await create_board(db, board)
        return {
            "message": "새로운 보드 생성을 성공했습니다.",
            "result": {
                "id": new_board.id,
                "user_id": new_board.user_id,
                "board_name": new_board.board_name,
                "image_url": new_board.image_url,
                "category_ratio": new_board.category_ratio,
                "keyword": new_board.keyword,
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보드 생성 중 오류 발생: {str(e)}"
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
                    "created_at": board.created_at
                }
                for board in boards
            ]
        }
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
        }
    }
