from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from typing import Optional
from app.models.SelectedChannelsRequest import SelectedChannelsRequest
from app.utils.utils import youtube_api_request

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])

@router.post("/channel-send")
def get_selected_channels(
    request_body: SelectedChannelsRequest,
    authorization: Optional[str] = Header(None, description="Bearer Token (Access Token)")
):
    if not authorization:
        return JSONResponse(status_code=401, content={
            "message": "로그인이 필요합니다.",
            "result": None
        })
    token_parts = authorization.split()
    if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
        return JSONResponse(status_code=401, content={
            "message": "유효하지 않은 Authorization 헤더입니다.",
            "result": None
        })
    access_token = token_parts[1]

    channel_ids = ",".join(request_body.selected_channels)
    params = {"part": "snippet", "id": channel_ids}
    data = youtube_api_request("channels", access_token, params)

    if "error" in data:
        return JSONResponse(status_code=401, content={
            "message": "유효하지 않은 YouTube OAuth 토큰입니다.",
            "result": None
        })

    channels_info = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        channel_info = {
            "채널이름": snippet.get("title"),
            "채널설명": snippet.get("description")
        }
        channels_info.append(channel_info)

    return JSONResponse(status_code=200, content={
        "message": "선택한 채널 정보를 성공적으로 가져왔습니다.",
        "result": channels_info
    })
