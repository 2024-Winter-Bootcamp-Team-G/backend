from google.cloud import storage
import requests


def upload_image_to_gcs(image_url: str, destination_path: str) -> str:
    """
    GCS에 이미지를 업로드하는 함수

    Args:
        image_url (str): 업로드할 이미지의 URL 또는 로컬 파일 경로
        destination_path (str): GCS 내 저장 경로

    Returns:
        str: 업로드된 GCS URL
    """
    bucket_name = "team-g-bucket"  # GCS 버킷 이름

    try:
        # GCS 클라이언트 초기화
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)

        # 이미지 다운로드 또는 로컬 파일 읽기
        if image_url.startswith("http"):
            print(f"이미지 다운로드 시도: {image_url}")
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"이미지 다운로드 실패: {response.status_code}")
            image_data = response.content
        else:
            print(f"로컬 파일 읽기 시도: {image_url}")
            with open(image_url, "rb") as f:
                image_data = f.read()

        # GCS에 업로드
        print(f"GCS 업로드 시도: 버킷={bucket_name}, 경로={destination_path}")
        blob = bucket.blob(destination_path)
        blob.upload_from_string(image_data, content_type="image/jpeg")

        # 업로드된 URL 반환
        gcs_url = f"https://storage.googleapis.com/{bucket_name}/{destination_path}"
        print(f"GCS 업로드 성공: {gcs_url}")
        return gcs_url

    except Exception as e:
        print(f"GCS 업로드 실패: {str(e)}")
        raise