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
                keywords={item["category"]: item["keywords"]}
            )
            session.add(new_data)
        session.commit()

    @staticmethod
    def get_keywords_from_db(session: Session, category: str):
        """
        특정 카테고리의 키워드 데이터를 DB에서 조회
        """
        data = session.query(Board).filter(Board.keywords.has_key(category)).first()  # JSON 키로 필터링
        if not data:
            raise ValueError(f"카테고리 '{category}'에 해당하는 데이터가 없습니다.")
        return {"category": category, "keywords": data.keywords.get(category)}
