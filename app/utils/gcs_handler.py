from google.cloud import storage
import requests
import tempfile


def upload_image_to_gcs(image_url: str, destination_path: str) -> str:
    """
    GCS에 이미지를 업로드하는 함수
    :param image_url: DALL·E에서 생성된 이미지 URL
    :param destination_path: GCS 내 저장 경로
    :return: 업로드된 이미지의 GCS URL
    """
    client = storage.Client()
    bucket_name = "team-g-bucket"
    bucket = client.bucket(bucket_name)

    # 이미지 다운로드
    response = requests.get(image_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to download image: {image_url}")

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        # GCS에 업로드
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(temp_file.name)

    # GCS URL 반환
    gcs_url = f"https://storage.googleapis.com/{bucket_name}/{destination_path}"
    return gcs_url
