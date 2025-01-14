from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate
from app.utils.redis_handler import RedisHandler
from app.utils.gpt_handler import classify_videos_with_gpt


async def create_board(db: Session, board_data: BoardCreate):
    """
    Redis에서 raw 데이터 가져오기 -> GPT 처리 -> DB 저장 (DALL·E는 추후 구현)
    """
    # 1. Redis에서 raw 데이터 가져오기
    # try:
    #     raw_data = RedisHandler.get_youtube_raw_data(board_data.redis_key)
    # except ValueError as e:
    #     raise ValueError(f"Redis 데이터 오류: {str(e)}")

    # 2. GPT를 통해 키워드와 카테고리 생성
    # try:
    #     classification_result = classify_videos_with_gpt(raw_data)
    #     keywords = classification_result["keyword"]
    #     category_ratio = classification_result["category_ratio"]
    #     board_name = ", ".join(keywords.keys())  # 키워드를 기반으로 보드 이름 생성
    # except Exception as e:
    #     raise ValueError(f"GPT 처리 오류: {str(e)}")

    # 3. DALL·E를 통한 이미지 생성 (추후 구현)
    image_url = None  # Placeholder: DALL·E 로직은 추후 추가

    # 4. DB 저장
    new_board = Board(
        user_id=board_data.user_id,
        board_name=board_name,
        image_url=image_url,
        category_ratio=category_ratio,
        keyword=keywords,
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return {
        "message": "보드가 성공적으로 생성되었습니다.",
        "board": {
            "id": new_board.id,
            "board_name": new_board.board_name,
            "category_ratio": new_board.category_ratio,
            "keyword": new_board.keyword,
        },
    }


# 모든 보드 조회
def get_boards(db: Session):
    return db.query(Board).all()


# 보드 상세 조회
def get_board_by_id(db: Session, board_id: int):
    return db.query(Board).filter(Board.id == board_id).first()
