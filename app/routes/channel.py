from unittest import result

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import requests
from app.config import GoogleConfig
from app.utils.redis_handler import RedisHandler

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])

youtube_api_key = GoogleConfig.API_KEY


@router.post("/channel-send")
def get_channel_info(channel_ids: list[str] = Query(..., description="채널 ID 목록")):
    search_endpoint = "https://www.googleapis.com/youtube/v3/search"
    results = []

    for channel_id in channel_ids:
        search_params = {
            "part": "snippet",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": 10,
            "key": youtube_api_key,
        }

        response = requests.get(search_endpoint, params=search_params)
        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "message": f"YouTube API 호출에 실패했습니다. (채널 ID: {channel_id})",
                    "error": response.json(),
                },
            )

        data = response.json()
        video_list = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_info = {
                "동영상제목": snippet.get("title"),
                "동영상설명": snippet.get("description"),
            }
            video_list.append(video_info)

        # Redis에 저장
        redis_key = f"youtube_videos:{channel_id}"
        RedisHandler.save_to_redis(redis_key, video_list)

        results.append({"채널ID": channel_id, "최신동영상목록": video_list})

    return JSONResponse(
        status_code=200,
        content={
            "message": "채널 최신 동영상 목록을 성공적으로 가져왔습니다.",
            "result": results
        },
    )