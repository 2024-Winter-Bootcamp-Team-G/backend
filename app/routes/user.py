from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLoginResponse,
    UserLoginRequest,
)
from app.utils import hash_password, verify_password
from app.services.user_service import login_user, logout_user
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Users"])


@router.get("/")
def get_users():
    return {"message": "List of users"}


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    # 비밀번호 해싱 및 사용자 생성
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        user_name=user.user_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/check-email")
def check_email(email: str, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일")
    return {"message": "이메일 사용 가능"}


@router.post("/login", response_model=UserLoginResponse)
def login(user: UserLoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user and verify_password(user.password, db_user.hashed_password) == True:
        tokens = login_user(db_user, db)
        return JSONResponse(
            status_code=200,
            content={
                "message": "로그인 성공.",
                "result": {
                    "user_id": db_user.id,
                    "token": {
                        "access": tokens["access_token"],
                        "refresh": tokens["refresh_token"],
                    },
                    "email": db_user.email,
                },
            },
        )
    else:
        return JSONResponse(
            status_code=401,
            content={
                "message": "이메일 또는 비밀번호가 잘못되었습니다.",
                "result": None,
            },
        )


@router.post("/logout")
def logout(refresh_token: str):
    try:
        logout_user(refresh_token)
        return {"message": "로그아웃 성공"}

    except HTTPException as e:
        raise e
