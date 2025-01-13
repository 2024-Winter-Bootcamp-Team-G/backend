from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base
from datetime import datetime
import pytz  # 패키지 설치 필요

KST = pytz.timezone("Asia/Seoul")  # 시간대 한국으로 설정


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=False)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(KST))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )
