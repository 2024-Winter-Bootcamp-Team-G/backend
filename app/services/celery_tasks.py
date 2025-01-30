from app.utils.celery_app import celery_app
from app.db import SessionLocal
from app.models.board import Board
from app.services.board_service import (
    fetch_cached_videos,
    fetch_videos_from_api,
    fetch_video_details,
    process_channel_data,
    generate_image_with_dalle,
    upload_image_to_gcs,
)
import time
from urllib.parse import urlparse

@celery_app.task(name="app.services.celery_tasks.create_board_task")
def create_board_task(user_id: int, board_id: int, channel_ids: list):
    """
    Celery Task: 보드 생성 비동기 작업
    """

    db = SessionLocal()  # Celery Task 내부에서 DB 세션 생성

    try:
        # Step 1: DB에서 보드 객체 가져오기
        board = db.query(Board).filter(Board.id == board_id).first()
        if not board:
            raise ValueError(f"보드 ID {board_id}를 찾을 수 없습니다.")


        # Step 2: YouTube 데이터 처리
        results = []
        cached_results = fetch_cached_videos(channel_ids)

        for channel_id in channel_ids:
            if channel_id in cached_results:
                results.append(cached_results[channel_id])
            else:
                video_ids = fetch_videos_from_api(board_id, channel_id)
                video_details = fetch_video_details(video_ids)
                results.append({"channel_id": channel_id, "videos": video_details})


        # Step 3: OpenAI GPT 키워드 및 카테고리 생성
        gpt_result = process_channel_data(channel_ids)
        category_ratio = gpt_result.get("category_ratio", [])
        keywords = gpt_result.get("keywords", {})
        board_name = gpt_result.get("board_name", "Generated Board")

        # Step 4: DALL·E 이미지 생성
        try:
            image_url = generate_image_with_dalle(category_ratio, keywords)
            parsed_url = urlparse(image_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"생성된 이미지 URL이 유효하지 않습니다: {image_url}")
        except Exception as e:
            raise ValueError(f"DALL·E 이미지 생성 오류: {str(e)}")

        # Step 5: GCS 업로드
        max_retries = 3
        gcs_image_url = None
        for attempt in range(max_retries):
            try:
                gcs_image_url = upload_image_to_gcs(
                    image_url, f"boards/{board.id}/{user_id}.png"
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"GCS 업로드 실패, 재시도 중 ({attempt + 1}/{max_retries})...")
                    time.sleep(2)
                else:
                    raise ValueError(f"GCS 업로드 오류: {str(e)}")

        # Step 6: 보드 데이터 업데이트
        board.image_url = gcs_image_url
        board.category_ratio = category_ratio
        board.keywords = keywords
        board.board_name = board_name
        db.commit()

        return {
            "board_id": board_id,
            "category_ratio": category_ratio,
            "keywords": keywords,
            "gcs_image_url": gcs_image_url,
        }

    except Exception as e:
        print(f"[ERROR] create_board_task 오류 발생: {str(e)}")
        return {"error": str(e)}

    finally:
        db.close()
