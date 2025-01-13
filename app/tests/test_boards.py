import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models.board import Board
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # 테스트 데이터 삽입
    test_board = Board(
        board_name="Test Board",
        category_ratio={"Music": 30, "Sports": 70},
        image_url="https://example.com/image.png",
        keyword={"Music": ["Rock", "Pop"], "Sports": ["Football", "Tennis"]},
        created_at=datetime.now(),
    )
    db.add(test_board)
    db.commit()
    db.refresh(test_board)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_board(setup_database):
    test_board_data = {
        "board_name": "테스트 보드",
        "category_ratio": {"Music": 30, "Sports": 70},
        "image_url": "https://example.com/image.png",
        "keyword": {"Music": ["Rock", "Pop"], "Sports": ["Football", "Tennis"]},
    }
    response = client.post("/boards/", json=test_board_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "새로운 보드 생성을 성공했습니다."


def test_get_boards(setup_database):
    response = client.get("/boards/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "보드 목록 조회에 성공했습니다."
    assert len(data["result"]["board"]) > 0


def test_get_board_detail(setup_database):
    response = client.get("/boards/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "요청한 보드 정보가 성공적으로 반환되었습니다."
    assert data["result"]["board"]["board_name"] == "Test Board"
