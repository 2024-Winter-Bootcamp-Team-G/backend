import requests
from app.config import GoogleConfig
from app.utils.redis_handler import RedisHandler
import json

youtube_api_key = GoogleConfig.API_KEY


def fetch_channel_info(channel_ids: list[str]) -> list[dict]:
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

    return results


def fetch_cached_videos(channel_ids: list[str]) -> list[dict]:
    results = []
    for channel_id in channel_ids:
        redis_key_channel = f"youtube_channel:{channel_id}"
        cached_video_ids = RedisHandler.get_from_redis(redis_key_channel)

        if cached_video_ids:
            latest_videos = (
                cached_video_ids
                if isinstance(cached_video_ids, list)
                else json.loads(cached_video_ids)
            )
            results.append(
                {
                    "채널ID": channel_id,
                    "최신동영상목록": latest_videos,
                    "is_cached": True,
                }
            )
        else:
            results.append(
                {"채널ID": channel_id, "최신동영상목록": [], "is_cached": False}
            )
    return results


def fetch_videos_from_api(channel_id: str) -> list[str]:
    search_params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "type": "video",
        "maxResults": 2,  # 테스트를 위한 제한
        "key": youtube_api_key,
    }

    search_response = requests.get(
        "https://www.googleapis.com/youtube/v3/search", params=search_params
    )

    if search_response.status_code != 200:
        raise ValueError(f"YouTube API 호출에 실패했습니다. (채널 ID: {channel_id})")

    search_data = search_response.json()
    video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]

    # 데이터 캐싱
    redis_key_channel = f"youtube_channel:{channel_id}"
    RedisHandler.save_to_redis(redis_key_channel, json.dumps(video_ids))

    return video_ids


def fetch_video_details(video_ids: list[str]) -> list[dict]:
    max_tags = 6
    max_desc_length = 300
    video_endpoint = "https://www.googleapis.com/youtube/v3/videos"
    video_details = []

    for i in range(0, len(video_ids), 50):  # YouTube API 제한으로 50개씩 처리
        chunk_ids = video_ids[i : i + 50]
        video_params = {
            "part": "snippet, contentDetails, statistics",
            "id": ",".join(chunk_ids),
            "key": youtube_api_key,
        }

        video_response = requests.get(video_endpoint, params=video_params)
        if video_response.status_code != 200:
            raise ValueError(
                f"YouTube API 호출에 실패했습니다. (Video IDs: {chunk_ids})"
            )

        video_data = video_response.json()
        for video in video_data.get("items", []):
            snippet = video.get("snippet", {})
            video_info = {
                "tags": snippet.get("tags", [])[:max_tags],
                "categoryId": snippet.get("categoryId"),
                "localizedTitle": snippet.get("localized", {}).get("title"),
                "localizedDescription": snippet.get("localized", {}).get(
                    "description", ""
                )[:max_desc_length],
            }

            # Redis에 저장
            redis_key_video = f"youtube_video:{video['id']}"
            RedisHandler.save_to_redis(redis_key_video, json.dumps(video_info))
            video_details.append(video_info)

    return video_details
