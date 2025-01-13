from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.board import BoardCreate
from app.services.board_service import get_boards, get_board_by_id, create_board
from app.db import get_db

router = APIRouter(prefix="/boards", tags=["Boards"])


# 보드 생성
@router.post("/", response_model=dict)
def create_new_board(board: BoardCreate, db: Session = Depends(get_db)):
    new_board = create_board(db, board)
    return {
        "message": "새로운 보드 생성을 성공했습니다.",
        "result": {
            "id": new_board.id,
            "board_name": new_board.board_name,
            "created_at": new_board.created_at,
        }
    }


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
