from fastapi import Query
from fastapi.responses import JSONResponse
import requests
from app.config import GoogleConfig
from app.utils.redis_handler import RedisHandler
import json

youtube_api_key = GoogleConfig.API_KEY

def fetch_channel_info(channel_ids: list[str] = Query(..., description="채널 ID 목록")):
    search_endpoint = "https://www.googleapis.com/youtube/v3/search"
    video_endpoint = "https://www.googleapis.com/youtube/v3/videos"
    max_video_ids_per_request = 50  # YouTube API 제한에 따라 50개씩 처리
    max_tag_count = 6  # 태그 최대 갯수 제한
    max_description_length = 300  # 설명 최대 길이 제한
    results = []

    for channel_id in channel_ids:
        # Redis에서 채널 동영상 목록 확인
        redis_key_channel = f"youtube_channel:{channel_id}"
        cached_video_ids = RedisHandler.get_from_redis(redis_key_channel)

        if cached_video_ids:
            # Redis에서 가져온 데이터가 이미 리스트일 경우 처리
            if isinstance(cached_video_ids, list):
                latest_videos = cached_video_ids
            else:
                # 문자열로 저장되어 있다면 JSON 파싱
                latest_videos = json.loads(cached_video_ids)

            results.append(
                {
                    "채널ID": channel_id,
                    "최신동영상목록": latest_videos,
                }
            )
            continue

        # YouTube API를 호출하여 최신 동영상 ID 가져오기
        search_params = {
            "part": "snippet",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": 2,  # 테스트시 가져올 동영상 개수 제한
            "key": youtube_api_key,
        }

        search_response = requests.get(search_endpoint, params=search_params)
        if search_response.status_code != 200:
            return JSONResponse(
                status_code=search_response.status_code,
                content={
                    "message": f"YouTube API 호출에 실패했습니다. (채널 ID: {channel_id})",
                    "error": search_response.json(),
                },
            )

        search_data = search_response.json()
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]

        if not video_ids:
            results.append(
                {
                    "채널ID": channel_id,
                    "최신동영상목록": [],
                }
            )
            continue

        # Redis에 최신 동영상 ID 목록 저장
        RedisHandler.save_to_redis(redis_key_channel, json.dumps(video_ids))

        # 동영상 세부 정보 요청 및 Redis 저장
        for i in range(0, len(video_ids), max_video_ids_per_request):
            chunk_ids = video_ids[i : i + max_video_ids_per_request]
            video_params = {
                "part": "snippet, contentDetails, statistics",
                "id": ",".join(chunk_ids),
                "key": youtube_api_key,
            }

            video_response = requests.get(video_endpoint, params=video_params)
            if video_response.status_code != 200:
                return JSONResponse(
                    status_code=video_response.status_code,
                    content={
                        "message": f"YouTube API 호출에 실패했습니다. (Video IDs {chunk_ids})",
                        "error": video_response.json(),
                    },
                )

            video_data = video_response.json()
            video_details = []

            for video in video_data.get("items", []):
                snippet = video.get("snippet", {})
                video_info = {
                    "tags": snippet.get("tags", [])[:max_tag_count],
                    "categoryId": snippet.get("categoryId"),
                    "localizedTitle": snippet.get("localized", {}).get("title"),
                    "localizedDescription": snippet.get("localized", {}).get(
                        "description", ""
                    )[:max_description_length],
                }

                # Redis에 동영상 세부 정보 저장
                redis_key_video = f"youtube_video:{video['id']}"
                RedisHandler.save_to_redis(redis_key_video, json.dumps(video_info))
                video_details.append(video_info)

            results.append(
                {
                    "채널ID": channel_id,
                    "최신동영상목록": video_details,
                }
            )

    return JSONResponse(
        status_code=200,
        content={
            "message": "채널 최신 동영상 목록과 상세 정보를을 성공적으로 가져왔습니다.",
            "result": results,
        },
    )
