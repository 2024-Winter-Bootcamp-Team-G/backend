import openai
from app.config import settings

openai.api_key = settings.openai_api_key


def classify_videos_with_gpt(video_data: str) -> dict:
    """OpenAI GPT를 사용하여 동영상 데이터를 분류"""
    prompt = f"""
    아래는 유튜브 동영상 데이터입니다. 각 동영상을 카테고리로 분류하고,
    각 카테고리의 비율을 계산한 뒤, 카테고리별 키워드 3개를 생성하세요.

    데이터: {video_data}

    형식:
    {{
        "category_ratio": {{"Category1": 50, "Category2": 50}},
        "keyword": {{"Category1": ["Keyword1", "Keyword2"], "Category2": ["Keyword3", "Keyword4"]}}
    }}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return eval(response["choices"][0]["message"]["content"])  # JSON 파싱
    except Exception as e:
        raise RuntimeError(f"OpenAI 요청 실패: {str(e)}")
