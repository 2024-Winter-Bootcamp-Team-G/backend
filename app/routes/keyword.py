from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.redis_handler import RedisHandler
from app.utils.gpt_handler import generate_keywords_and_category
from app.utils.db_handler import DBHandler
from app.db import get_db
import json

router = APIRouter(prefix="/gpt", tags=["GPT"])


@router.post("/keywords/{video_id}")
async def get_keywords_for_video(
        video_ids: list[str],
        db: Session = Depends(get_db)
):
    if len(video_ids) > 10:
        return {"error": "최대 10개의 video_id만 처리할 수 있습니다."}

    video_data_list = []

    # 선택한 video_id의 데이터 가져오기
    for video_id in video_ids:
        redis_key = f"youtube_video:{video_id}"
        try:
            video_data = RedisHandler.get_value(redis_key)
            if not video_data:
                return {"error": f"Redis에서 video_id {video_id} 데이터를 찾을 수 없습니다."}
            video_data_list.append(json.loads(video_data))  # JSON 디코딩 후 리스트에 추가
        except Exception as e:
            return {"error": f"Redis에서 video_id {video_id} 데이터 로드 중 오류 발생: {str(e)}"}

    # GPT 호출
    try:
        gpt_result = await generate_keywords_and_category(video_data_list)
    except Exception as e:
        return {"error": f"GPT 처리 중 오류 발생: {str(e)}"}

    # 결과를 DB에 저장
    try:
        DBHandler.save_gpt_response_to_db(
            db,
            data=gpt_result,
            user_id=3  # 테스트용 user_id, db에 존재하는 user_id로 기입
        )
    except Exception as e:
        return {"error": f"DB 저장 실패: {str(e)}"}

    return {"status": "success", "data": gpt_result}
