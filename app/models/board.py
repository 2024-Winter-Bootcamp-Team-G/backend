from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import pytz, uuid

KST = pytz.timezone("Asia/Seoul")


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_name = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    category_ratio = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(KST), nullable=True)

    # Relationship
    user = relationship("User", back_populates="boards")