from sqlalchemy.orm import Session
from app.models import Board

class DBHandler:
    @staticmethod
    def save_gpt_response_to_db(session: Session, data: dict | list[dict], user_id: int):
        if isinstance(data, dict):  # 딕셔너리
            data = [data]  # 리스트로 변환하고 처리

        for item in data:
            new_data = Board(
                user_id=user_id,
                category=item["category"],
                keywords=item["keywords"]
            )
            session.add(new_data)
        session.commit()

    @staticmethod
    def get_keywords_from_db(session: Session, category: str):
        data = session.query(Board).filter(Board.category == category).first()
        if not data:
            raise ValueError(f"카테고리 '{category}'에 해당하는 데이터가 없습니다.")
        return {"category": data.category, "keywords": data.keywords}
