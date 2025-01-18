from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate
from app.utils import RedisHandler
from app.utils.dalle_handler import generate_image_with_dalle
from app.utils.gcs_handler import upload_image_to_gcs
from app.utils.gpt_handler import generate_keywords_and_category
from urllib.parse import urlparse
import time
from app.services.channel_service import fetch_channel_info, fetch_cached_videos, fetch_video_details,fetch_videos_from_api


# 보드 생성
async def create_board(db: Session, board_data: BoardCreate, user_id: int, channel_ids:list ) -> Board:
    # 채널 ID 목록 가져오기
    # 2. 유튜브 API 호출 및 Redis 저장
    # TODO: 유튜브 API를 호출하여 채널 정보와 최신 동영상 목록을 Redis에 저장하는 로직 구현 필요
    # channel_service의 함수 호출
    results = []

    # Step 1: Redis 캐시 확인
    cached_results = fetch_cached_videos(channel_ids)
    
    for result in cached_results:
        channel_id = result["채널ID"]

        # 캐시된 데이터 있으면 바로 추가
        if result["is_cached"]:
            results.append(result)
            continue

        # Step 2: API 호출하여 동영상 ID 가져오기
        video_ids = fetch_videos_from_api(channel_id)
        if not video_ids:
            results.append({"채널ID": channel_id, "최신동영상목록": []})
            continue

        # redis 캐싱 확인

        # Step 3: 동영상 세부 정보 가져오기
        video_details = fetch_video_details(video_ids)

        results.append({"채널ID": channel_id, "최신동영상목록": video_details})

    # 2. 유튜브 API 호출 및 Redis 저장
    # TODO: 유튜브 API를 호출하여 채널 정보와 최신 동영상 목록을 Redis에 저장하는 로직 구현 필요

    
    # 3. Redis에서 데이터 가져오기 및 GPT 키워드 생성
    # TODO: Redis에서 데이터를 가져와 GPT로 키워드와 카테고리를 생성하는 로직 구현 필요
    channel_ids = ["ch1", "ch2", "ch3", "ch4", "ch5"]  # 더미 채널ID, 병합 후 삭제 얘종
    board_name = (
        board_data.board_name or "Generated Board"
    )  # 보드 이름도 gpt가 생성해주어야 하긴 한데...

    gpt_result = await process_channel_data(channel_ids)
    category_ratio = gpt_result.get("category_ratio", [])
    keywords = gpt_result.get("keywords", {})

    # 4. DALL·E를 통한 이미지 생성
    try:
        image_url = generate_image_with_dalle(category_ratio, keywords)
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"생성된 이미지 URL이 유효하지 않습니다: {image_url}")

    except Exception as e:
        raise ValueError(f"DALL·E 이미지 생성 오류: {str(e)}")

    # TODO: GCS 저장 로직 검증 필요
    max_retries = 3
    for attempt in range(max_retries):
        try:
            gcs_image_url = upload_image_to_gcs(
                image_url, f"boards/{user_id}/{board_name}.png"
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"GCS 업로드 실패, 재시도 중 ({attempt + 1}/{max_retries})...")
                time.sleep(2)
            else:
                raise ValueError(f"GCS 업로드 오류: {str(e)}")

    # 5. DB 저장
    new_board = Board(
        user_id=user_id,
        board_name=board_data.board_name,
        image_url=gcs_image_url,
        category_ratio=category_ratio,
        keywords=keywords,
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return {
        "board": {
            "id": new_board.id,
            "board_name": new_board.board_name,
            "category_ratio": new_board.category_ratio,
            "keywords": new_board.keywords,
        },
    }

# 모든 보드 조회
def get_boards(db: Session, user_id: int):
    return db.query(Board).filter(Board.user_id == user_id).all()


# 보드 상세 조회
def get_board_by_id(db: Session, board_id: int):
    return db.query(Board).filter(Board.id == board_id).first()


async def process_channel_data(channel_ids: list[str]):
    """
    Redis에서 데이터 가져오기 및 GPT 키워드 생성

    Args:
        channel_ids (list[str]): 처리할 채널 ID 목록

    Returns:
        dict: GPT 결과 (카테고리 비율과 키워드)
    """
    try:
        video_data_list = []  # GPT로 보낼 동영상 데이터를 저장할 리스트

        for channel_id in channel_ids:
            # Redis에서 채널 ID 기반 최신 동영상 목록 가져오기
            redis_channel_key = f"youtube_channel:{channel_id}"
            video_ids = RedisHandler.get_from_redis(redis_channel_key)

            if not video_ids:
                print(f"Redis에 채널 ID {channel_id}의 동영상 데이터가 없습니다.")
                continue

            # Redis에서 각 동영상 ID의 세부 정보 가져오기
            for video_id in video_ids:
                redis_video_key = f"youtube_video:{video_id}"
                video_data = await RedisHandler.get_from_redis(redis_video_key)
                if video_data:
                    video_data_list.append(video_data)

        if not video_data_list:
            raise ValueError("GPT로 보낼 데이터가 없습니다.")

        gpt_result = await generate_keywords_and_category(video_data_list)
        return gpt_result

    except Exception as e:
        raise ValueError(f"Redis 또는 GPT 처리 오류: {str(e)}")
