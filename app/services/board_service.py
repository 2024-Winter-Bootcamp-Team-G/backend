import uuid, time, json
from typing import Any

from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardResponse
from app.utils import RedisHandler
from app.utils.dalle_handler import generate_image_with_dalle, delete_image_from_gcs
from app.utils.gcs_handler import upload_image_to_gcs
from app.utils.gpt_handler import generate_keywords_and_category
from urllib.parse import urlparse
from app.services.channel_service import (
    fetch_cached_videos,
    fetch_video_details,
    fetch_videos_from_api,
)


# 보드 생성
async def create_board(
    db: Session, user_id: int, channel_ids: list
) -> dict:
    # 1. DB에 Board 먼저 생성 (ID 확보)
    new_board = Board(
        user_id=user_id,
        uuid=str(uuid.uuid4()),
        board_name="Generated Board",
        image_url="",
        category_ratio=[],
        keywords={},
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)  # board_id 확보

    # 2. 채널 데이터 처리
    results = []

    # Redis 캐시 확인
    cached_results = fetch_cached_videos(channel_ids)

    for result in cached_results:
        channel_id = result["채널ID"]

        # 캐시된 데이터 있으면 바로 추가
        if result["is_cached"]:
            results.append(result)
            continue

        # API 호출하여 동영상 ID 가져오기
        video_ids = fetch_videos_from_api(new_board.id, channel_id)
        if not video_ids:
            results.append({"채널ID": channel_id, "최신동영상목록": []})
            continue

        # redis 캐싱 확인

        # 동영상 세부 정보 가져오기
        video_details = fetch_video_details(video_ids)

        results.append({"채널ID": channel_id, "최신동영상목록": video_details})

    # 3. Redis에서 데이터 가져오기 및 GPT 키워드 생성
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

    # 5. GCS 업로드
    max_retries = 3
    gcs_image_url = None
    for attempt in range(max_retries):
        try:
            gcs_image_url = upload_image_to_gcs(
                image_url, f"boards/{new_board.id}/{user_id}.png"
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"GCS 업로드 실패, 재시도 중 ({attempt + 1}/{max_retries})...")
                time.sleep(2)
            else:
                raise ValueError(f"GCS 업로드 오류: {str(e)}")

    # step 6. DB 저장
    new_board.image_url = gcs_image_url
    new_board.category_ratio = category_ratio
    new_board.keywords = keywords
    db.commit()

    return {
        "board": {
            "id": new_board.id,
        },
    }


def get_board_by_uuid(db: Session, board_uuid: str):
    """
    보드 UUID를 사용하여 보드 데이터를 가져옵니다.
    """
    return db.query(Board).filter(Board.uuid == board_uuid).first()


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
                video_data = RedisHandler.get_from_redis(redis_video_key)
                if not video_data:
                    print(f"Redis에 동영상 ID {video_id}의 데이터가 없습니다.")
                    continue
                video_data_list.append(video_data)

        if not video_data_list:
            raise ValueError("GPT로 보낼 데이터가 없습니다.")

        try:
            print(f"GPT에 전송할 채널 리스트: {video_data_list}")
            gpt_result = await generate_keywords_and_category(video_data_list)
            print(f"GPT에서 받은 데이터: {gpt_result}")
            return gpt_result
        except Exception as e:
            print(f"GPT 키워드 생성 중 오류: {str(e)}")
            raise ValueError(f"키워드 재생성 오류: {str(e)}")

    except Exception as e:
        raise ValueError(f"Redis 또는 GPT 처리 오류: {str(e)}")


# 키워드 재생성
async def regenerate_keywords(db: Session, board_id: int, user_id: int):
    """
    보드의 키워드를 재생성하며, 보드별 Redis 데이터를 기반으로 GPT 요청.
    """
    board = get_board_by_id(db, board_id)

    if not board:
        raise ValueError("Board not found")

    if board.user_id != user_id:
        raise ValueError("권한이 없습니다.")

    try:
        # Redis에서 해당 보드의 채널 ID 목록 가져오기
        redis_board_key = f"board_videos:{board_id}"
        video_ids = RedisHandler.get_from_redis(redis_board_key)

        if not video_ids:
            raise ValueError(f"Redis에 보드 ID {board_id}의 동영상 데이터가 없습니다.")

        # Redis에서 각 동영상 ID의 세부 정보 가져오기
        video_data_list = []
        for video_id in video_ids:
            redis_video_key = f"youtube_video:{video_id}"
            video_data = RedisHandler.get_from_redis(redis_video_key)
            if not video_data:
                print(f"Redis에 동영상 ID {video_id}의 데이터가 없습니다.")
                continue
            video_data_list.append(video_data)

        if not video_data_list:
            raise ValueError("GPT로 보낼 데이터가 없습니다.")

        # GPT를 통해 키워드 및 카테고리 생성
        gpt_result = await generate_keywords_and_category(video_data_list)
        new_keywords = gpt_result.get("keywords", {})

        # 키워드 갱신
        board.keywords = json.dumps(new_keywords, ensure_ascii=False)

        # 변경사항 저장
        db.commit()
        db.refresh(board)

        return {
            "board_id": board.id,
            "new_keywords": new_keywords,
        }

    except Exception as e:
        raise ValueError(f"키워드 재생성 오류: {str(e)}")

# 이미지 재생성
def regenerate_image(board_id: int, user_id: int, db: Session):
    """
    이미지를 재생성하고 GCS 및 DB를 업데이트하는 함수
    :param board_id: 재생성할 보드의 ID
    :param user_id: 요청한 사용자의 ID
    :param db: 데이터베이스 세션
    """
    # 1. 기존 보드 정보 가져오기
    board = db.query(Board).filter(Board.id == board_id, Board.user_id == user_id).first()
    if not board:
        raise ValueError("해당 보드를 찾을 수 없습니다.")

    # 2. 기존 이미지 삭제 (선택 사항, 필요 시 GCS에서 삭제)
    if board.image_url:
        image_url_value = str(board.image_url)  # 문자열로 명시적 변환
        try:
            delete_image_from_gcs(image_url_value)
        except Exception as e:
            print(f"기존 이미지 삭제 오류: {str(e)}")
    else:
        print("보드에 이미지 URL이 없습니다.")

    # 3. DALL·E를 통한 새로운 이미지 생성
    try:
        # `board.category_ratio`와 `board.keywords` 값을 Python 기본 타입으로 변환
        category_ratio = json.loads(board.category_ratio) if isinstance(board.category_ratio,
                                                                        str) else board.category_ratio
        keywords = json.loads(board.keywords) if isinstance(board.keywords, str) else board.keywords

        # 이미지 생성
        new_image_url = generate_image_with_dalle(category_ratio, keywords)
        parsed_url = urlparse(new_image_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"재생성된 이미지 URL이 유효하지 않습니다: {new_image_url}")
    except Exception as e:
        raise ValueError(f"DALL·E 이미지 재생성 오류: {str(e)}")



    # 4. 새로운 이미지 GCS 업로드
    max_retries = 3
    gcs_image_url = None
    for attempt in range(max_retries):
        try:
            gcs_image_url = upload_image_to_gcs(
                new_image_url, f"boards/{user_id}/{board.board_name}.png"
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"GCS 업로드 실패, 재시도 중 ({attempt + 1}/{max_retries})...")
                time.sleep(2)
            else:
                raise ValueError(f"GCS 업로드 오류: {str(e)}")

    # 5. DB 업데이트
    board.image_url = gcs_image_url
    db.commit()
    print(f"이미지가 재생성되고 업데이트되었습니다: {gcs_image_url}")

    return gcs_image_url