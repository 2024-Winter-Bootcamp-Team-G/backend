from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(KST), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )

    # Relationship
    boards = relationship("Board", back_populates="user")
