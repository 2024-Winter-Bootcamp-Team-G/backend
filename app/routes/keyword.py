from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.redis_handler import RedisHandler
from app.utils.gpt_handler import generate_keywords_for_video
from app.utils.image_generator import generate_images_from_keywords
from app.utils.db_handler import DBHandler
from app.db import get_db
from app.schemas.gpt import SaveKeywordsRequest
import json

router = APIRouter(prefix="/gpt", tags=["GPT"])

async def generate_keywords_from_redis(channel_id: str) -> dict:
    redis_key = f"youtube_keywords:{channel_id}"

    # Redis에 기존에 저장된 키워드 데이터 확인
    cached_data = RedisHandler.get_value(redis_key)
    if cached_data:
        return json.loads(cached_data)

    # Redis에서 동영상 리스트 가져오기
    redis_video_key = f"youtube_video:{channel_id}"
    try:
        video_list = RedisHandler.get_youtube_raw_data(redis_video_key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"동영상 데이터가 없습니다: {str(e)}")

    # 여러 동영상 데이터를 하나의 프롬프트로 GPT에 전달하여 카테고리 및 키워드 추출
    try:
        classification_results = await generate_keywords_for_video()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 생성 실패: {str(e)}")

    # 추후 캐시를 위해 Redis에 결과 저장 가능
    # RedisHandler.set_value(redis_key, json.dumps(classification_results))

    return classification_results

@router.get("/keywords/{video_id}")
async def get_keywords_for_video(video_id: str):
    try:
        result = await generate_keywords_for_video(video_id)
        return {"video_id": video_id, "result": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keywords/save")
async def save_keywords(
    request: SaveKeywordsRequest,  # Pydantic 모델로 변경
    db: Session = Depends(get_db)
):
    try:
        # 데이터 저장 로직
        DBHandler.save_gpt_response_to_db(
            db,
            {
                "category": request.category,
                "keywords": request.keywords
            },
            user_id=request.user_id  # 테스트용이라 user_id 1만 입력 가능, 변경 OK
        )
        return {"message": "카테고리와 키워드가 성공적으로 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")

@router.get("/keywords/{board_id}/images")
async def generate_images(category: str, db: Session = Depends(get_db)):
    try:
        # PostgreSQL에서 데이터 불러오기
        data = DBHandler.get_keywords_from_db(db, category)

        # 데이터 구조 변환: {카테고리: [키워드 목록]}
        keywords_by_category = {data["category"]: data["keywords"]}

        # DALL·E를 이용해 이미지 생성
        images = generate_images_from_keywords(keywords_by_category)

        return {"category": category, "images": images}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")