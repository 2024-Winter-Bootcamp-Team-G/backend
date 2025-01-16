import json
from sqlalchemy.orm import Session
from app.utils.redis_handler import RedisHandler
from app.utils.gpt_handler import generate_keywords_for_video
from app.models.board import Board


def process_and_store_video_data(db: Session, redis_key: str, board_id: int):
    """Redis에서 데이터를 가져와 GPT로 처리 후 DB에 저장"""
    # Redis에서 raw data 가져오기
    raw_data = RedisHandler.get_youtube_raw_data(redis_key)
    if not raw_data:
        raise ValueError(f"Redis에서 {redis_key} 키에 해당하는 데이터가 없습니다.")

    # GPT로 데이터 분류
    classification_result = generate_keywords_for_video(raw_data)
    classification_dict = json.loads(classification_result)

    # DB에 저장
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise ValueError(f"Board ID {board_id}가 존재하지 않습니다.")

    board.category_ratio = classification_dict.get("category_ratio")
    board.keyword = classification_dict.get("keyword")
    db.commit()
    db.refresh(board)

    return {
        "message": "동영상 데이터를 성공적으로 분류하고 저장했습니다.",
        "board_id": board.id,
        "category_ratio": board.category_ratio,
        "keyword": board.keyword,
    }
