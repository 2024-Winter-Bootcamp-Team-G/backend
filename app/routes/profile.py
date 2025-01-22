from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from google.cloud import storage
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
import os
import uuid
from app.config import settings
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.put("/upload") # put
def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # 사용자 데이터베이스에서 검색
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="사용자 정보를 찾을 수 없습니다.",
        )

    # GCS 클라이언트 초기화
    client = storage.Client.from_service_account_json(settings.gcp_credentials)
    bucket = client.get_bucket(settings.gcp_bucket_name)

    # 파일 검증 및 경로 설정
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension.lower() not in {".jpg", ".jpeg", ".png"}:
        return JSONResponse(
            status_code=400,
            content={
                "message": "지원되지 않는 파일 형식입니다.",
                "result": None,
            },
        )

    blob_name = f"user/{user_id}/{uuid.uuid4()}{file_extension}"
    blob = bucket.blob(blob_name)

    # 파일 업로드
    blob.upload_from_file(file.file, content_type=file.content_type)
    blob.make_public()
    public_url = blob.public_url

    # DB에 URL 저장
    user.profile_img_url = public_url
    db.commit()

    return {
        "message": "프로필 사진이 업로드 되고 URL이 저장되었습니다.",
        "profile_img_url": public_url
    }


@router.get("/{user_id}")
async def get_profile_picture(user_id: str, folder: str = "profile_pictures"):
    """
    Google Cloud Storage에서 프로필 사진 URL 반환
    """
    try:
        # 1. GCS 클라이언트 초기화
        print("Initializing Google Cloud Storage client...")
        client = storage.Client.from_service_account_json(settings.gcp_credentials)
        bucket = client.get_bucket(settings.gcp_bucket_name)
        print(f"Connected to GCS bucket: {settings.gcp_bucket_name}")

        # 2. 파일 경로 검색
        prefix = f"{folder}/{user_id}/"
        print(f"Searching for files in GCS path: {prefix}")
        blobs = list(bucket.list_blobs(prefix=prefix))
        print(f"Found blobs: {[blob.name for blob in blobs]}")

        if not blobs:
            print("No blobs found in the specified GCS path.")
            return JSONResponse(
                status_code=404,
                content={
                    "message": "프로필 사진을 찾을 수 없습니다.",
                    "result": None,
                },
            )

        # 3. 최신 파일 선택
        blob = max(blobs, key=lambda b: b.updated)
        print(f"Selected blob: {blob.name}, last updated at: {blob.updated}")

        # 4. Public URL 가져오기
        print("Fetching public URL...")
        public_url = blob.public_url
        print(f"Public URL: {public_url}")

        # 5. 결과 반환
        return {
            "message": "프로필 url을 성공적으로 반환했습니다.",
            "url": public_url
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "서버 내부 오류가 발생했습니다.",
                "error": str(e),
            },
        )

