from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate
from app.utils.dalle_handler import generate_image_with_dalle
from app.utils.gcs_handler import upload_image_to_gcs

# from app.utils.redis_handler import RedisHandler
# from app.utils.gpt_handler import extract_keywords_video


# 보드 생성
async def create_board(db: Session, board_data: BoardCreate, user_id: int):
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

    # # 임시 데이터
    # keywords = {"example": "keyword"}
    # category_ratio = [70, 30]
    board_name = board_data.board_name or "Generated Board"

    # 3. DALL·E를 통한 이미지 생성
    try:
        existing_board = db.query(Board).filter(Board.user_id == user_id).first()
        category_ratio = existing_board.category_ratio
        keywords = existing_board.keywords
        image_url = generate_image_with_dalle(category_ratio, keywords)
    except Exception as e:
        raise ValueError(f"DALL·E 이미지 생성 오류: {str(e)}")
    try:
        gcs_image_url = upload_image_to_gcs(
            image_url, f"boards/{user_id}/{board_name}.png"
        )
    except Exception as e:
        raise ValueError(f"GCS 업로드 오류: {str(e)}")

    # 4. DB 저장
    new_board = Board(
        user_id=user_id,
        board_name=board_data.board_name,
        image_url=gcs_image_url,
        category_ratio=category_ratio,
        keywords=keywords,
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
            "keywords": new_board.keywords,
        },
    }


# 모든 보드 조회
def get_boards(db: Session, user_id: int):
    return db.query(Board).filter(Board.user_id == user_id).all()


# 보드 상세 조회
def get_board_by_id(db: Session, board_id: int):
    return db.query(Board).filter(Board.id == board_id).first()
