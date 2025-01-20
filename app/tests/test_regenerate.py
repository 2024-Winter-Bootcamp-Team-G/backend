import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
print("Env loaded successfully.")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Board
from app.services.board_service import regenerate_image

# 실제 데이터베이스 및 GCS에 연결하기 위한 설정
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@host:port/dbname")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def setup_board_data(db_session):
    board = Board(
        id=1,
        user_id=1,
        board_name="Test Board",
        image_url="https://example.com/old_image.png",
        category_ratio='[40, 30, 20, 10]',
        keywords='{"Wildlife": ["Lions", "Elephants"], "Landscapes": ["Mountains", "Rivers"]}'
    )
    db_session.add(board)
    db_session.commit()
    return board

def test_regenerate_image_actual(db_session, setup_board_data):
    board_id = setup_board_data.id
    user_id = setup_board_data.user_id

    # 실제 regenerate_image 함수 호출 (모킹 제거)
    try:
        new_image_url = regenerate_image(board_id, user_id, db_session)
        print(f"새 이미지 URL: {new_image_url}")
        assert new_image_url is not None
    except Exception as e:
        pytest.fail(f"regenerate_image 호출 중 오류 발생: {e}")
