from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.redis_handler import redis_client
import json

router = APIRouter(prefix="/preferences", tags=["Channel Preferences"])


@router.get("/channel-collect")
def get_subscriptions(data_id: str):
    # Redis에서 구독 데이터 가져오기
    redis_key = f"subscriptions:{data_id}"
    cached_data = redis_client.get(redis_key)

    if not cached_data:
        raise HTTPException(status_code=422, detail="Google login required")

    # Redis에서 가져온 데이터 반환
    result = json.loads(cached_data)
    return JSONResponse(
        status_code=200,
        content={
            "message": "구독 채널 목록을 성공적으로 가져왔습니다.",
            "result": result,
        },
    )
