import pytest
from app.utils.gcs_handler import upload_image_to_gcs
from google.cloud import storage
import os

CREDENTIALS_PATH = "../../gcp-key.json"


@pytest.mark.parametrize(
    "image_url, destination_path",
    [
        (
            "https://via.placeholder.com/150",  # 테스트용 샘플 이미지 URL
            "test-folder/test-image.jpg",  # GCS 내 업로드 경로
        )
    ],
)
def test_upload_image_to_gcs(image_url, destination_path):
    """
    GCS에 이미지를 업로드하고 업로드된 URL을 확인하는 테스트
    """
    try:
        gcs_url = upload_image_to_gcs(image_url, destination_path)
        print(f"Uploaded Image URL: {gcs_url}")
        assert gcs_url.startswith(
            "https://storage.googleapis.com/"
        ), "Invalid GCS URL format"
        assert destination_path in gcs_url, "Destination path is not in the GCS URL"
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}")


def test_gcs_connection():
    """
    GCS 연결을 확인하는 테스트
    """
    bucket_name = "team-g-bucket"

    try:
        client = storage.Client.from_service_account_json(CREDENTIALS_PATH)
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket {bucket.name} is accessible.")
    except Exception as e:
        pytest.fail(f"GCS connection failed: {str(e)}")


def test_local_image_upload_to_gcs():
    """
    로컬 이미지 파일을 GCS에 업로드하는 테스트
    """
    local_file_path = "./test.png"
    destination_path = "test-folder/local-test-image.png"

    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    with open(local_file_path, "wb") as f:
        f.write(os.urandom(1024))

    try:
        gcs_url = upload_image_to_gcs(local_file_path, destination_path)
        print(f"Uploaded Local Image URL: {gcs_url}")
        assert gcs_url.startswith(
            "https://storage.googleapis.com/"
        ), "Invalid GCS URL format"
        assert destination_path in gcs_url, "Destination path is not in the GCS URL"
    except Exception as e:
        pytest.fail(f"Local image upload test failed: {str(e)}")
    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
