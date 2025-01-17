from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import pytz

KST = pytz.timezone("Asia/Seoul")


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_name = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    category_ratio = Column(JSON, nullable=False)
    keywords = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(KST), nullable=False)

    # Relationship
    user = relationship("User", back_populates="boards")