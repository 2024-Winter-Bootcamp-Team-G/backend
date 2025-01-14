from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.utils.utils import youtube_api_request
from app.utils.redis_handler import redis_client
import json

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])

@router.get("/channel-collect")
def get_subscriptions(access_token: str):
    # Redis 캐싱 키
    redis_key = f"subscriptions:{access_token}"

    # Redis에서 캐싱된 데이터 확인
    cached_data = redis_client.get(redis_key)
    if cached_data:
        print("Redis에서 데이터 가져옴")
        # Redis에서 가져온 데이터 반환
        return JSONResponse(status_code=200, content={
            "message": "구독 채널 목록을 성공적으로 가져왔습니다. (캐시 사용)",
            "result": json.loads(cached_data)  # JSON 문자열을 파이썬 객체로 변환
        })

    params = {"part": "snippet", "mine": "true", "maxResults": 50}
    data = youtube_api_request("subscriptions", access_token, params)

    if "error" in data:
        return JSONResponse(
            status_code=401,
            content={
                "message": "유효하지 않은 토큰 또는 오류가 발생했습니다.",
                "result": None,
            },
        )

    result = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        channel_info = {
            "채널이름": snippet.get("title"),
            "채널ID": snippet.get("resourceId", {}).get("channelId"),
            "채널이미지": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        }
        result.append(channel_info)

    return JSONResponse(
        status_code=200,
        content={
            "message": "구독 채널 목록을 성공적으로 가져왔습니다.",
            "result": result,
        },
    )
