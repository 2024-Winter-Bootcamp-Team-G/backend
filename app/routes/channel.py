from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import requests
from app.config import GoogleConfig

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])

youtube_api_key = GoogleConfig.API_KEY


@router.post("/channel-send")
def get_channel_info(channel_ids: list[str] = Query(..., description="채널 ID 목록")):
    endpoint = "https://www.googleapis.com/youtube/v3/channels"
    channel_id_list = ",".join(channel_ids)
    params = {
        "part": "snippet,statistics",
        "id": channel_id_list,
        "key": youtube_api_key,
    }

    response = requests.get(endpoint, params=params)
    if response.status_code != 200:
        return JSONResponse(
            status_code=response.status_code,
            content={
                "message": "YouTube API 호출에 실패했습니다.",
                "error": response.json(),
            },
        )

    data = response.json()
    result = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        channel_info = {
            "채널이름": snippet.get("title"),
            "채널설명": snippet.get("description"),
        }
        result.append(channel_info)

    return JSONResponse(
        status_code=200,
        content={"message": "채널 정보를 성공적으로 가져왔습니다.", "result": result},
    )
