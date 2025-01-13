import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models.user import User
from datetime import datetime

client = TestClient(app)

# 테스트용 데이터베이스 세팅
@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # 테스트 데이터 삽입
    test_user = User(
        email="test@example.com",
        hashed_password="hashedpassword123",
        user_name="testuser",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# 회원가입 테스트 (성공)
def test_signup_success(setup_database):
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "user_name": "newuser"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["user_name"] == user_data["user_name"]
    assert "id" in data


# 이메일 중복 테스트
def test_signup_duplicate_email(setup_database):
    user_data = {
        "email": "test@example.com",  # 이미 존재하는 이메일
        "password": "newpassword123",
        "user_name": "anotheruser"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 존재하는 이메일입니다."


# 이메일 사용 가능 여부 확인 테스트
def test_check_email_available(setup_database):
    email = "available@example.com"
    response = client.post("/auth/check-email", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == "이메일 사용 가능"


# 이미 사용 중인 이메일 확인 테스트
def test_check_email_taken(setup_database):
    email = "test@example.com"  # 이미 사용 중인 이메일
    response = client.post("/auth/check-email", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 사용 중인 이메일"