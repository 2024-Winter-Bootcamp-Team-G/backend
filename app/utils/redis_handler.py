import redis
import json
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, decode_responses=True
)


class RedisHandler:
    @staticmethod
    def save_to_redis(key: str, new_videos: list[dict], expire: int = 3600):
        try:
            # 기존 데이터를 가져옴
            existing_data = redis_client.get(key)
            if existing_data:
                existing_videos = json.loads(existing_data)
            else:
                existing_videos = []

            # 중복 제거: 새로운 동영상만 필터링
            unique_videos = [
                video for video in new_videos if video not in existing_videos
            ]

            # 기존 데이터와 병합 후 저장
            combined_videos = existing_videos + unique_videos
            redis_client.set(key, json.dumps(combined_videos), ex=expire)

            print(f"Redis에 {key} 저장 완료 (중복 제거 후 {len(unique_videos)}개 저장).")
        except Exception as e:
            print(f"Redis 저장 실패: {e}")


    @staticmethod
    def get_from_redis(key: str):
        """
        Redis에서 데이터를 가져오기
        """
        try:
            raw_data = redis_client.get(key)
            if not raw_data:
                return None
            return json.loads(raw_data)
        except Exception as e:
            print(f"Redis에서 데이터 가져오기 실패: {e}")
            return None


    @staticmethod
    def get_youtube_raw_data(key: str):
        """
        Redis에서 YouTube RAW 데이터를 가져오기
        """
        raw_data = redis_client.get(key)
        if not raw_data:
            raise ValueError(f"Redis에 '{key}' 키에 해당하는 데이터가 없습니다.")
        # JSON 문자열을 다시 Python 리스트나 딕셔너리로 변환
        return json.loads(raw_data)

    # 저장
    def set_key_value(key: str, value: str, expire: int = 3600):
        redis_client.set(key, value, ex=expire)

    # 불러오기
    def get_value(key: str) -> str:
        return redis_client.get(key)

    # 삭제
    def delete_key(key: str):
        redis_client.delete(key)
