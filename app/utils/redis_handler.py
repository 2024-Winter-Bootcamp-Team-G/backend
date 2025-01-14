import redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, decode_responses=True
)


class RedisHandler:
    @staticmethod
    def get_youtube_raw_data(key: str):
        """
        Redis에서 YouTube RAW 데이터를 가져오기
        """
        raw_data = redis_client.get(key)
        if not raw_data:
            raise ValueError(f"Redis에 '{key}' 키에 해당하는 데이터가 없습니다.")
        return raw_data
