import json
from openai import AsyncOpenAI
from app.config import settings

async def generate_keywords_and_category(video_data_list: list[dict]) -> dict:
    # 여러 video_id의 데이터를 선택해 프롬프트로 전달
    prompt = f"""
    Below is a variety of videos selected. The use of each field is as follows::
    1. tags and category ID (cate) and category ID (cate) is used when extract categories.
    2. Title (localized Title) and description (localizedDes) is used when extracting keywords.

    Analysis of data:
    - Generate the name of each category and 3 related keywords in Korean.
    - Calculates the ratio of each category based on all data.

    동영상 데이터:
    {json.dumps(video_data_list, ensure_ascii=False, indent=2)}

    출력 형식:
    {{
      "category_ratio": [25, 25, 30, 20],
      "keywords": {{
          "category1": ["키워드1", "키워드2", "키워드3"],
          "category2": ["키워드1", "키워드2", "키워드3"],
          "category3": ["키워드1", "키워드2", "키워드3"],
          "category4": ["키워드1", "키워드2", "키워드3"]
      }}
    }}
    """
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")