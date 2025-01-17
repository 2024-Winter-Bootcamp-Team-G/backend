from google.cloud import storage


def test_gcs_connection():
    bucket_name = "team-g-bucket"  # 버킷 이름
    credentials_path = "../../gcp-key.json"

    # GCS 클라이언트 생성
    client = storage.Client.from_service_account_json(credentials_path)
    bucket = client.get_bucket(bucket_name)
    print(f"Bucket {bucket.name} is accessible.")


test_gcs_connection()
