from fastapi import APIRouter, HTTPException, Depends, status
from app.models import Board
from app.utils.redis_handler import redis_client
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.board_service import get_board_by_id, get_boards
from app.services.user_service import get_current_user

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.post("/share")
async def share_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    자신의 공유하려는 사용자가 자신의 보드를 공유하기 위해 URL을 생성합니다.
    """
    try:
        # 해당 보드가 현재 사용자 소유인지 확인
        board = get_board_by_id(db, board_id)
        if not board:
            raise HTTPException(status_code=404, detail="해당 보드를 찾을 수 없습니다.")
        if board.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="해당 보드에 대한 권한이 없습니다."
            )

        # Redis에 공유 링크 설정 (TTL: 1시간)
        redis_key = f"shared_link:{board.uuid}"
        redis_client.set(redis_key, board_id, ex=3600)

        # 공유 링크 반환
        shared_url = f"http://localhost:8000/boards/shared/{board.uuid}"
        return {
            "message": "공유 링크가 성공적으로 생성되었습니다.",
            "result": {"shared_url": shared_url},
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"링크 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/shared/{board_uuid}", response_model=dict)
def get_shared_board_and_user_boards(
    board_uuid: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    공유된 보드와 현재 사용자의 보드 목록 반환
    Args:
        board_uuid (str): 공유된 보드의 UUID
        db (Session): 데이터베이스 세션
        current_user (dict): 현재 사용자 정보
    Returns:
        dict: 공유된 보드와 현재 사용자의 보드 목록
    """
    try:
        # 공유된 보드 가져오기
        shared_board = db.query(Board).filter(Board.uuid == board_uuid).first()

        if not shared_board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="공유된 보드를 찾을 수 없습니다.",
            )

        # 현재 사용자의 보드 목록 가져오기
        user_boards = db.query(Board).filter(Board.user_id == current_user["id"]).all()

        # 반환 데이터 구성
        return {
            "message": "공유된 보드와 사용자 보드 목록이 성공적으로 반환되었습니다.",
            "result": {
                "shared_board": {
                    "id": shared_board.id,
                    "board_name": shared_board.board_name,
                    "category_ratio": shared_board.category_ratio,
                    "keywords": shared_board.keywords,
                },
                "user_boards": [
                    {
                        "id": board.id,
                        "board_name": board.board_name,
                        "created_at": board.created_at,
                    }
                    for board in user_boards
                ],
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 반환 중 오류 발생: {str(e)}",
        )
