from app.db import engine, Base, SessionLocal
from app.models.board import Board
from app.models.user import User
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 샘플 데이터 삽입
def init_db():
    db = SessionLocal()  # SessionLocal()로 세션 객체 생성
    try:
        # Users 데이터 추가
        user_1 = User(
            email="user1@example.com",
            hashed_password="hashedpassword1",
            user_name="User One",
            created_at=datetime.now(KST),
            updated_at=datetime.now(KST),
        )
        user_2 = User(
            email="user2@example.com",
            hashed_password="hashedpassword2",
            user_name="User Two",
            created_at=datetime.now(KST),
            updated_at=datetime.now(KST),
        )
        db.add_all([user_1, user_2])
        db.commit()

        # Boards 데이터 추가
        board_1 = Board(
            user_id=1,
            board_name="Sample Board 1",
            created_at=datetime.now(KST),
        )
        board_2 = Board(
            user_id=2,
            board_name="Sample Board 2",
            created_at=datetime.now(KST),
        )
        db.add_all([board_1, board_2])
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during initialization: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
