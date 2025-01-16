import json
from app.utils.redis_handler import redis_client


def get_video_data(video_id: str) -> dict:
    key = f"youtube_video:{video_id}"
    data = redis_client.get(key)
    if data:
        try:
            # 첫 번째 JSON 디코딩 시도
            result = json.loads(data)

            # 결과가 리스트인지 확인
            if isinstance(result, list) and all(isinstance(item, str) for item in result):
                # 리스트가 문자들의 리스트인 경우 이를 하나의 문자열로 결합
                joined = "".join(result)
                # 결합된 문자열을 다시 JSON으로 디코딩
                result = json.loads(joined)

            # 결과가 리스트라면 첫 번째 요소 선택
            if isinstance(result, list):
                if result:
                    result = result[0]
                else:
                    raise ValueError(f"키 {key}에 저장된 리스트가 비어 있습니다.")

            # 결과가 딕셔너리인지 확인
            if not isinstance(result, dict):
                raise ValueError(f"키 {key}의 데이터가 dict 또는 list가 아님")
            return result
        except json.JSONDecodeError:
            raise ValueError(f"키 {key}의 데이터 파싱 실패")
    else:
        raise ValueError(f"키 {key}에 해당하는 데이터가 없습니다.")
