from fastapi.testclient import TestClient
from app.main import app
from app.utils.redis_handler import RedisHandler
import redis
import json

client = TestClient(app)

def setup_module(module):
    """
    Redis에 더미 데이터 삽입
    """
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    dummy_data = {
        "kind": "youtube#videoListResponse",
        "items": [{"id": "uJLqYB8npDc", "snippet": {"title": "테스트 영상"}}],
    }
    redis_client.set("youtube_raw_data", json.dumps(dummy_data))

def test_redis_handler():
    """
    RedisHandler 테스트
    """
    raw_data = RedisHandler.get_youtube_raw_data("youtube_raw_data")
    assert raw_data is not None
    parsed_data = json.loads(raw_data)
    assert "items" in parsed_data

def test_fastapi_redis_route():
    """
    FastAPI 라우트 테스트
    """
    response = client.get("/test/redis?redis_key=youtube_raw_data")
    assert response.status_code == 200
    assert response.json()["message"] == "Redis 데이터 읽기 성공"
