from google.cloud import storage
import requests


def upload_image_to_gcs(
    image_url: str, destination_path: str, credentials_path: str = "../../gcp-key.json"
) -> str:
    """
    GCS에 이미지를 업로드하는 함수

    Args:
        image_url (str): 업로드할 이미지의 URL 또는 로컬 파일 경로
        destination_path (str): GCS 내 저장 경로
        credentials_path (str): GCP 서비스 계정 키 파일 경로

    Returns:
        str: 업로드된 GCS URL
    """
    bucket_name = "team-g-bucket"  # GCS 버킷 이름

    # GCS 클라이언트 초기화
    client = storage.Client.from_service_account_json(credentials_path)
    bucket = client.get_bucket(bucket_name)

    # 이미지 다운로드 또는 로컬 파일 읽기
    if image_url.startswith("http"):
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
    else:
        with open(image_url, "rb") as f:
            image_data = f.read()

    # GCS에 업로드
    blob = bucket.blob(destination_path)
    blob.upload_from_string(image_data, content_type="image/jpeg")

    # 업로드된 URL 반환
    gcs_url = f"https://storage.googleapis.com/{bucket_name}/{destination_path}"
    return gcs_url
