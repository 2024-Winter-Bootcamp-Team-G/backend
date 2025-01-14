from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.utils import hash_password

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
