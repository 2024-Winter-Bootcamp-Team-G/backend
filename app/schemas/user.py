from pydantic import BaseModel, EmailStr, Field, ConfigDict


class User(BaseModel):
    id: int
    name: str
    email: str


# 회원가입 요청
class UserCreate(BaseModel):
    # 이메일 형식이 아닌 데이터는 오류처리
    email: EmailStr = Field(..., max_length=50)
    password: str
    user_name: str = Field(..., max_length=50)


# 회원가입 응답
class UserResponse(BaseModel):
    id: int
    email: EmailStr = Field(..., max_length=50)
    user_name: str = Field(..., max_length=50)

    model_config = ConfigDict(from_attributes=True)
