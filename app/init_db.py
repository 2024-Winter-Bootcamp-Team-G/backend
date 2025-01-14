from app.db import SessionLocal, engine, Base
from app.models.board import Board
from datetime import datetime

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)


# 샘플 데이터 삽입
def init_db():
    db = SessionLocal()
    try:
        # 샘플 데이터 추가
        sample_board_1 = Board(
            # user_id=1,
            board_name="Sample Board 1",
            created_at=datetime(),
        )
        sample_board_2 = Board(
            # user_id=2,
            board_name="Sample Board 2",
            created_at=datetime(),
        )

        # 데이터 삽입
        db.add(sample_board_1)
        db.add(sample_board_2)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
