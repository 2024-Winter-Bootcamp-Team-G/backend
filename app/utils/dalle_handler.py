from google.cloud import storage
from openai import OpenAI
from app.config import settings
from urllib.parse import urlparse
from google.auth import default

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
        f"""
        Create an image inspired by classic 35mm film photography. The image should evoke a nostalgic, cinematic atmosphere with warm, natural light and soft, grainy textures.
        1. An image inspired by classic 35mm film photography, featuring a warm off-white hue and subtle grainy texture. The overall composition should capture a timeless, cinematic quality with natural imperfections characteristic of analog film.
        2. Use slightly desaturated colors with natural tones, warm undertones, and soft lighting to evoke a nostalgic feel. The lighting should feel authentic and balanced to highlight the objects in the composition.
        3. Include 3 to 4 objects based on all the keywords below, ensuring they are spaced apart with clear intervals while maintaining a harmonious composition.: 

        {', '.join(prompt_parts)}

        # Output Format:
        - Image Description: [Provide a brief description of the generated image.]
        - Main Colors: [List 3-5 dominant colors used in the image.]
        - Mood: [Describe the overall mood of the image.]
        """
    )

    try:
        response = client.images.generate(
            model="dall-e-3",
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

# 이미지 재생성 시 기존 이미지 삭제
def delete_image_from_gcs(image_url: str):
    """
    GCS에서 이미지를 삭제하는 함수
    :param image_url: 삭제할 이미지의 GCS URL
    """
    bucket_name = "team-g-bucket"
    try:
        # URL 파싱 및 검증
        parsed_url = urlparse(image_url)
        if not parsed_url.path.startswith(f"/{bucket_name}/"):
            raise ValueError(f"Invalid GCS URL: {image_url}")

        # Blob 이름 추출
        blob_name = parsed_url.path.split(f"/{bucket_name}/")[-1]

        # GCS 클라이언트 초기화
        credentials, project = default()
        client = storage.Client(credentials=credentials, project=project)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Blob 존재 여부 확인 및 삭제
        if blob.exists():
            blob.delete()
            print(f"GCS에서 이미지가 삭제되었습니다: {blob_name}")
        else:
            print(f"GCS에서 해당 이미지를 찾을 수 없습니다: {blob_name}")
    except Exception as e:
        raise RuntimeError(f"GCS 이미지 삭제 중 오류 발생: {str(e)}")
