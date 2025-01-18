from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.channel_service import fetch_channel_info

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])
@router.post("/channel-send")
def channel_send(channel_ids: list[str] = Query(..., description="채널 ID 목록")):
    data = fetch_channel_info(channel_ids)
    return JSONResponse(content=data, status_code=200)