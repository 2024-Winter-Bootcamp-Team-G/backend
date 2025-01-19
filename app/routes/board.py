from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.board import BoardCreate
from app.services.board_service import get_boards, get_board_by_id, create_board
from app.db import get_db
from app.services.user_service import decode_access_token
from fastapi.security import OAuth2PasswordBearer
import json
from app.utils.gpt_handler import match_board_ratio
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/boards", tags=["Boards"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    JWT 토큰에서 현재 사용자 정보 추출
    """
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    email = payload.get("sub")
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return {"email": email, "id": user_id}


@router.post("", status_code=201)
async def create_new_board(
    board_data: BoardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    channel_ids: list[str] = Query(..., description="채널 ID 목록"),
):
    """
    보드 생성:
    1. Redis에서 raw 데이터를 가져옴.
    2. GPT로 카테고리 및 키워드를 생성.
    3. 생성된 키워드/카테고리를 기반으로 이미지를 생성.
    4. 결과를 DB에 저장.
    """

    try:
        result = await create_board(db=db, board_data=board_data, user_id=current_user["id"], channel_ids=channel_ids)
        return {"message": "보드가 성공적으로 생성되었습니다."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보드 생성 중 오류 발생: {str(e)}",
        )


# 보드 목록 조회
@router.get("", response_model=dict)
def read_boards(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    boards = get_boards(db, current_user["id"])
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

    print(f"[DEBUG] DB에서 가져온 카테고리 비율: {board.category_ratio}")
    print(f"[DEBUG] DB에서 가져온 키워드: {board.keywords}")

    return {
        "message": "요청한 보드 정보가 성공적으로 반환되었습니다.",
        "result": {
            "board": {
                "board_name": board.board_name,
                "image_url": board.image_url,
                "category_ratio": board.category_ratio,
                "keywords": board.keywords,
                "created_at": board.created_at,
            }
        },
    }


@router.post("/match-ratio")
async def board_match(
        board_id1: int,
        board_id2: int,
        db: Session = Depends(get_db)
        ):

    board1 = get_board_by_id(db, board_id1)
    board2 = get_board_by_id(db, board_id2)

    board_sum_list = [board1.keywords, board2.keywords]

    gpt_result = await match_board_ratio(board_sum_list)

    return JSONResponse(
        status_code=200,
        content={"message": "알고리즘 일치율 계산에 성공했습니다.",
                 "match_ratio": gpt_result,
                 "board1_category_ratio": board1.category_ratio,
                 "board2_category_ratio": board2.category_ratio
                 }
    )

