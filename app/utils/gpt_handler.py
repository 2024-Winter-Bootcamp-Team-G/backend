import json
from openai import AsyncOpenAI
from app.utils.redis_utils import get_video_data
from fastapi import HTTPException
from app.config import settings

async def generate_keywords_for_video(video_id: str) -> dict:
    try:
        video_data = get_video_data(video_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 디버깅: video_data의 타입과 내용 출력
    print(f"Type of video_data: {type(video_data)}")
    print(f"Content of video_data: {video_data}")

    # video_data가 리스트인 경우 처리
    if isinstance(video_data, list):
        if video_data:
            video_data = video_data[0]
            print("video_data was a list; using first element.")
        else:
            raise HTTPException(status_code=404, detail="동영상 데이터가 비어 있습니다.")

    # video_data가 딕셔너리가 맞는지 확인
    if not isinstance(video_data, dict):
        raise HTTPException(status_code=500, detail="예상하지 못한 데이터 형식입니다.")

    # 동영상 데이터로부터 필요한 정보 추출
    tags = video_data.get("tags", [])
    category_id = video_data.get("categoryId", "")
    title = video_data.get("localizedTitle", "")
    description = video_data.get("localizedDescription", "")

    # GPT 프롬프트 구성
    prompt = f"""
    아래의 태그와 카테고리 정보로 대표 카테고리를, 제목과 설명으로 대표 키워드 3개를 추출해 주세요.
    태그: {', '.join(tags)}
    카테고리 ID: {category_id}
    제목: {title}
    설명: {description}

    형식:
    {{
      "category": "카테고리명",
      "keywords": ["키워드1", "키워드2", "키워드3"]
    }}
    """
    content = ""
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        # 응답 데이터를 출력
        print("OpenAI API 응답:", response.choices[0].message.content)

        content = response.choices[0].message.content
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}. 응답 데이터: {content}")
    except Exception as e:
        raise RuntimeError(f"OpenAI 요청 실패: {str(e)}")
