import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.config import settings, RedisSettings
from app.models import User
from dotenv import load_dotenv
from app.utils import time_zone
from app.utils.redis_handler import RedisHandler

load_dotenv()


# JWT 토큰 생성 함수
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(time_zone()) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


# JWT 리프레시 토큰 생성 함수
def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(time_zone()) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def login_user(user: User, db):
    # 유효한 사용자일 경우
    if user:
        # 액세스 토큰 및 리프레시 토큰 생성
        access_token_expires = timedelta(minutes=RedisSettings.access_token_expire_minutes)
        refresh_token_expires = timedelta(minutes=RedisSettings.refresh_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        )

        # 리프레시 토큰을 Redis에 저장
        RedisHandler.set_key_value(f"refresh_token_{user.email}", refresh_token, expire=refresh_token_expires.seconds)
        return {"access_token": access_token, "refresh_token": refresh_token}

"""    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 로그인 정보",
            headers={"WWW-Authenticate": "Bearer"},
        )
"""

def logout_user(refresh_token: str):
    # 리프레시 토큰을 Redis에서 삭제
    decoded_refresh_token = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
    email = decoded_refresh_token.get("sub")

    if email:
        RedisHandler.delete_key(f"refresh_token_{email}")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 토큰")
