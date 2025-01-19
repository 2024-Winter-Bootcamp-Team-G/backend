from openai import OpenAI
from app.config import settings
import requests

client = OpenAI(api_key=settings.openai_api_key)


def generate_image_with_dalle(category_ratio: list[int], keywords: dict) -> str:
    """
    DALL·E를 사용하여 이미지를 생성하는 함수
    :param category_ratio: 각 카테고리의 비율 리스트 (예: [10, 20, 30, 10])
    :param keywords: 각 카테고리의 키워드 (예: {"category1": ["k1", "k2"], ...})
    :return: 생성된 이미지의 URL
    """
    # 프롬프트 생성
    categories = list(keywords.keys())
    if len(category_ratio) != len(categories):
        raise ValueError("category_ratio와 keywords의 길이가 일치하지 않습니다.")

    prompt_parts = []
    for i, category in enumerate(categories):
        ratio = category_ratio[i]
        category_keywords = ", ".join(keywords[category])
        prompt_parts.append(f"{category} ({ratio}%): {category_keywords}")
    prompt = (
        "You are a highly skilled illustrator drawing with Microsoft Paint. "
        "You need to create pixel-style images based on the provided categories and keywords. "
        "The images should look crude, with very low detail and rough lines. "
        "Use dark colors to create a dull tone. Place all the drawings on a single page freely.\n\n"
        "Draw pixelated illustrations based on the following themes:\n"
        + "; ".join(prompt_parts)
        + "\n\n"
        "# Output Format:\n"
        "- Image Description: [Provide a brief description of the generated image.]\n"
        "- Main Colors: [List 3-5 dominant colors used in the image.]\n"
        "- Mood: [Describe the overall mood of the image.]\n"
    )

    try:
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(f"Image generated successfully: {image_url}")
        return image_url
    except Exception as e:
        raise ValueError(f"Image generation failed: {str(e)}")
