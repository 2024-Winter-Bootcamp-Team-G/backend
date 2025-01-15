from sqlalchemy.orm import Session
from app.db import engine, Base, SessionLocal
from app.models.board import Board
from app.models.user import User
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 테이블 초기화
def reset_db(db: Session):
    db.query(Board).delete()  # Boards 테이블 데이터 삭제
    db.query(User).delete()  # Users 테이블 데이터 삭제
    db.commit()

# 샘플 데이터 삽입
def init_db():
    db = SessionLocal()  # 세션 생성
    try:
        reset_db(db)  # 기존 데이터 초기화

        # 1. Users 데이터 추가
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
        db.commit()  # Users 데이터 확정

        # 삽입된 User ID 가져오기
        user1_id = user_1.id
        user2_id = user_2.id

        # 2. Boards 데이터 추가
        board_1 = Board(
            user_id=user1_id,  # user_1의 ID
            board_name="Sample Board 1",
            created_at=datetime.now(KST),
        )
        board_2 = Board(
            user_id=user2_id,  # user_2의 ID
            board_name="Sample Board 2",
            created_at=datetime.now(KST),
        )
        db.add_all([board_1, board_2])
        db.commit()  # Boards 데이터 확정

    except Exception as e:
        db.rollback()
        print(f"Error during initialization: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()