from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from google.cloud import storage
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app. schemas.user import UpdateUserSchema, UpdatePasswordSchema
import os
import uuid
from app.config import settings
from fastapi.responses import JSONResponse
from app.services.user_service import get_current_user
from sqlalchemy import select
from app.utils import verify_password, hash_password
from app.services.user_service import logout_user
from app.utils.redis_handler import RedisHandler

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.put("/upload") # put
def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    # 현재 사용자 정보 가져오기
    user_id = current_user["id"]

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
async def get_profile_picture(current_user: dict = Depends(get_current_user)):

    # 현재 사용자 정보 가져오기
    user_id = current_user["id"]
    folder = "user"

    try:
        # 1. GCS 클라이언트 초기화\
        client = storage.Client.from_service_account_json(settings.gcp_credentials)
        bucket = client.get_bucket(settings.gcp_bucket_name)\

        # 2. 파일 경로 검색
        prefix = f"{folder}/{user_id}/"
        blobs = list(bucket.list_blobs(prefix=prefix))

        if not blobs:
            return JSONResponse(
                status_code=404,
                content={
                    "message": "프로필 사진을 찾을 수 없습니다.",
                    "result": None,
                },
            )

        # 3. 최신 파일 선택
        blob = max(blobs, key=lambda b: b.updated)
        public_url = blob.public_url

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

@router.put("/name_change")
def name_change(user_data: UpdateUserSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["id"]

    query = select(User).where(User.id == user_id)
    result = db.execute(query)
    user = result.scalars().first()

    if user_data.name:
        user.name = user_data.name

    db.add(user)
    db.commit()
    db.refresh(user)  # 업데이트된 데이터를 반환

    return JSONResponse(
        status_code=200,
        content={
            "message": "이름이 변경됐습니다.",
            "user_name": user_data.name
        },
    )


@router.put("/password_change")
def password_change(password_data: UpdatePasswordSchema, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["id"]

    query = select(User).where(User.id == user_id)
    result = db.execute(query)
    user = result.scalars().first()

    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")

    hashed_new_password = hash_password(password_data.new_password)

    user.hashed_password = hashed_new_password
    db.add(user)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={
            "message": "비밀번호가 성공적으로 변경되었습니다.",
            "result": None
        }
    )

