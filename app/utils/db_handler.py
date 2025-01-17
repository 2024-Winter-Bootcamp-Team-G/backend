from sqlalchemy.orm import Session
from app.models import Board
import json

class DBHandler:
    @staticmethod
    def save_gpt_response_to_db(session: Session, data: dict, user_id: int):
        """
        GPT에서 생성된 데이터를 Board 테이블에 저장
        :param session: SQLAlchemy 세션
        :param data: GPT에서 생성된 데이터 (category_ratio와 keywords 포함)
        :param user_id: 사용자 ID
        """
        try:
            # category_ratio와 keywords를 분리
            category_ratio = data.get("category_ratio")  # 리스트 [10, 20, 30, 40]
            keywords = data.get("keywords")  # JSON 형식 { "category1": [...], ... }

            if not category_ratio or not keywords:
                raise ValueError("category_ratio 또는 keywords가 데이터에 없습니다.")

            # Board 테이블에 저장
            new_board_entry = Board(
                user_id=user_id,
                category_ratio=json.dumps(category_ratio),  # 리스트를 JSON 문자열로 저장
                keywords=keywords  # JSON 형식 그대로 저장
            )
            session.add(new_board_entry)
            session.commit()

        except Exception as e:
            session.rollback()
            raise RuntimeError(f"DB 저장 실패: {str(e)}")