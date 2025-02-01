import redis
import json
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, decode_responses=True
)


class RedisHandler:
    @staticmethod
    def save_to_redis_list(key: str, new_videos: list[dict], expire: int = 3600):
        try:
            # 기존 데이터를 가져옴
            existing_data = redis_client.get(key)
            if existing_data:
                existing_videos = json.loads(existing_data)
            else:
                existing_videos = []

            # 새로운 데이터가 이미 JSON 문자열인 경우 처리
            if isinstance(new_videos, str):
                new_videos = json.loads(new_videos)

            # 중복 제거: 새로운 동영상만 필터링
            unique_videos = [
                video for video in new_videos if video not in existing_videos
            ]

            # 기존 데이터와 병합 후 저장
            combined_videos = existing_videos + unique_videos
            redis_client.set(key, json.dumps(combined_videos), ex=expire)

            print(
                f"Redis에 {key} 저장 완료 (중복 제거 후 {len(unique_videos)}개 저장)."
            )
        except Exception as e:
            print(f"Redis 저장 실패: {e}")

    @staticmethod
    def get_from_redis_list(key: str):
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
    def save_video_details_to_redis(redis_key: str, data: dict):
        """
        Redis에 딕셔너리 데이터를 저장하는 함수.

        Args:
            key (str): Redis 키
            data (dict): 저장할 데이터
        """
        try:
            for field, value in data.items():
                redis_client.hset(redis_key, field, json.dumps(value))
            print(f"데이터가 Redis에 저장되었습니다: {redis_key}")
        except Exception as e:
            raise ValueError(f"Redis 저장 중 오류 발생: {str(e)}")


    @staticmethod
    def get_video_details_from_redis(redis_key: str) -> dict:
        """
        Redis 해시에서 동영상 세부 정보를 가져오는 함수.

        Args:
            redis_key (str): Redis 키
        Returns:
            dict: Redis 해시에 저장된 데이터
        """
        try:
            # Redis 해시의 모든 필드를 가져옴
            data = redis_client.hgetall(redis_key)
            print(f"[DEBUG] REDIS 해시 조회: {data}")

            # JSON 문자열로 저장된 값을 디코딩
            return {field: json.loads(value) for field, value in data.items()}
        except Exception as e:
            print(f"Redis 가져오기 중 오류 발생: {e}")
            raise e


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
