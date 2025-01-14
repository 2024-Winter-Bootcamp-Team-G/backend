from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.utils.utils import youtube_api_request

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])

@router.get("/channel-collect")
def get_subscriptions(access_token: str):
    params = {"part": "snippet", "mine": "true", "maxResults": 50}
    data = youtube_api_request("subscriptions", access_token, params)

    if "error" in data:
        return JSONResponse(status_code=401, content={
            "message": "유효하지 않은 토큰 또는 오류가 발생했습니다.",
            "result": None
        })

    result = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        channel_info = {
            "채널프로필": snippet.get("thumbnails", {}).get("default", {}).get("url"),
            "채널이름": snippet.get("title"),
            "채널ID": snippet.get("resourceId", {}).get("channelId"),
            "채널이미지": snippet.get("thumbnails", {}).get("high", {}).get("url")
        }
        result.append(channel_info)

    return JSONResponse(status_code=200, content={
        "message": "구독 채널 목록을 성공적으로 가져왔습니다.",
        "result": result
    })
