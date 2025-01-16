import openai
from app.config import settings

openai.api_key = settings.openai_api_key

def generate_images_from_keywords(keywords_by_category: dict) -> dict:
    images = {}
    for category, keywords in keywords_by_category.items():
        images[category] = {}
        for keyword in keywords:
            prompt = f"{category} 관련 이미지: {keyword}"
            try:
                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size="256x256"
                )
                image_url = response["data"][0]["url"]
                images[category][keyword] = image_url
            except Exception as e:
                images[category][keyword] = f"이미지 생성 오류: {e}"
    return images