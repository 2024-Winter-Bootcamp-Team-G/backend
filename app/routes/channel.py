# from fastapi import APIRouter, Query
# from fastapi.responses import JSONResponse
# from app.services.channel_service import fetch_channel_info
#
# router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])
# @router.post("/channel-send")
# def channel_send(channel_ids: list[str] = Query(..., description="채널 ID 목록")):
#     data = fetch_channel_info(channel_ids)
#     return JSONResponse(content=data, status_code=200)
#
#
#
# #

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.services.channel_service import fetch_channel_info
from app.services.user_service import decode_access_token  # JWT 디코딩 유틸리티 필요

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    JWT 토큰에서 현재 사용자 정보 추출
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/channel-send")
def channel_send(
    channel_ids: list[str] = Query(..., description="채널 ID 목록"),
    user_id: int = Depends(get_current_user),
):
    """
    채널 ID와 사용자 ID를 기반으로 데이터를 처리합니다.
    """
    data = fetch_channel_info(user_id, channel_ids)
    return JSONResponse(content=data, status_code=200)