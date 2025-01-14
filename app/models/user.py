from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
from app.utils import time_zone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_name = Column(String(50), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(time_zone())
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(time_zone()),
        onupdate=lambda: datetime.now(time_zone()),
    )

    # Relationship
    boards = relationship("Board", back_populates="user")
