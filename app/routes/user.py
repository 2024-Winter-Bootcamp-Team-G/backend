from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLoginResponse
)
from app.utils import verify_password
from app.services.user_service import (
    login_user,
    logout_user,
    create_user,
    is_email_taken,
)
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Users"])


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if is_email_taken(user.email, db):
        return JSONResponse(
            status_code=400,
            content={"message": "이미 존재하는 이메일입니다.", "result": None},
        )

    # 사용자 생성 로직 호출
    new_user = create_user(user, db)
    return JSONResponse(
        status_code=201,
        content={
            "message": "회원가입 성공",
            "result": {
                "user_id": new_user.id,
                "email": new_user.email,
                "created_at": new_user.created_at.isoformat(),
            },
        },
    )


@router.get("/check-email")
def check_email(email: str, db: Session = Depends(get_db)):
    if is_email_taken(email, db):
        return JSONResponse(
            status_code=400,
            content={"message": "이미 존재하는 이메일입니다.", "result": False},
        )
    return JSONResponse(
        status_code=201,
        content={"message": "이메일 사용 가능", "result": True},
    )


@router.post("/login", response_model=UserLoginResponse)
def login(
    username: str = Form(...),  # OAuth2PasswordBearer에 맞게 수정
    password: str = Form(...),  # OAuth2PasswordBearer에 맞게 수정
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(User).filter(User.email == username).first()
    )  # username을 email로 사용
    if db_user and verify_password(password, db_user.hashed_password):
        tokens = login_user(db_user, db)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )


@router.post("/logout")
def logout(refresh_token: str):
    try:
        logout_user(refresh_token)
        return JSONResponse(
            status_code=200,
            content={
                "message": "로그아웃 성공",
                "result": None,
            },
        )

    except HTTPException as e:
        raise e
