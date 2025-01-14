import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.redis_handler import redis_client

client = TestClient(app)

@pytest.fixture
def setup_redis():
    """
    Redis 초기화 및 테스트 데이터 준비.
    """
    # Redis 클리어
    redis_client.flushdb()

    # Redis에 테스트 데이터 삽입
    redis_client.setex("shared_link:123", 3600, "https://example.com/shared-board/123")

    yield

    # 테스트 종료 후 Redis 데이터 삭제
    redis_client.flushdb()

def test_post_share(setup_redis):
    """
    POST /share 테스트: 공유 링크 생성.
    """
    board_id = 456
    response = client.post("/api/v1/share", json={"board_id": board_id})
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "보드 공유에 성공했습니다."
    assert "shared_link" in data["result"]

    # Redis에 링크가 저장되었는지 확인
    shared_link = redis_client.get(f"shared_link:{board_id}")
    assert shared_link == f"https://example.com/shared-board/{board_id}"

def test_get_shared_link(setup_redis):
    """
    GET /shared-link/{board_id} 테스트: 공유 링크 조회.
    """
    board_id = 123  # setup_redis에서 삽입한 데이터
    response = client.get(f"/api/v1/shared-link/{board_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "공유 링크 조회에 성공했습니다."
    assert data["result"]["shared_link"] == f"https://example.com/shared-board/{board_id}"

def test_get_nonexistent_shared_link(setup_redis):
    """
    GET /shared-link/{board_id} 테스트: 존재하지 않는 링크 조회.
    """
    board_id = 999  # Redis에 없는 데이터
    response = client.get(f"/api/v1/shared-link/{board_id}")
    assert response.status_code == 404

    data = response.json()
    assert data["detail"]["message"] == "공유 링크가 만료되었거나 존재하지 않습니다."
