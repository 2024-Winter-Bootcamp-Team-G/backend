import redis
import json
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, decode_responses=True
)


class RedisHandler:
    # 저장
    def set_key_value(key: str, value: str, expire: int = 3600):
        redis_client.set(key, value, ex=expire)

    # 불러오기
    def get_value(key: str) -> str:
        return redis_client.get(key)

    # 삭제
    def delete_key(key: str):
        redis_client.delete(key)
