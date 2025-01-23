import json
import requests
import uuid
from fastapi import HTTPException
from app.config import GoogleConfig
from app.utils.redis_handler import redis_client
from app.utils.utils import youtube_api_request


def exchange_code_for_token(code: str) -> str:
    token_url = GoogleConfig.GOOGLE_TOKEN_URL
    payload = {
        "client_id": GoogleConfig.CLIENT_ID,
        "client_secret": GoogleConfig.CLIENT_SECRET,
        "code": code,
        "redirect_uri": GoogleConfig.REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="토큰을 가져오는 데 실패했습니다.")

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=500, detail="Access token not found")

    return access_token


def get_cached_or_request_subscriptions(access_token: str):
    # data_id 만들기
    data_id = str(uuid.uuid4())
    redis_key = f"subscriptions:{data_id}"

    # Redis에서 캐싱된 데이터 확인
    cached_data = redis_client.get(redis_key)
    if cached_data:
        print("Redis에서 데이터 가져옴")
        return {
            "message": "구독 채널 목록을 성공적으로 가져왔습니다. (캐시 사용)",
            "result": json.loads(cached_data),
        }

    # YouTube API 요청
    params = {"part": "snippet", "mine": "true", "maxResults": 50}
    data = youtube_api_request("subscriptions", access_token, params)

    if "error" in data:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰 또는 오류가 발생했습니다.")

    # 채널 목록 반환
    result = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        channel_info = {
            "채널이름": snippet.get("title"),
            "채널ID": snippet.get("resourceId", {}).get("channelId"),
            "채널이미지": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        }
        result.append(channel_info)

    # Redis에 구독 데이터 저장
    redis_client.set(redis_key, json.dumps(result), ex=3600)  # 1시간 동안 캐싱 유지
    print(f"Redis에 데이터 저장 완료: {redis_key}")

    # data_id 반환
    return {"data_id": data_id}
