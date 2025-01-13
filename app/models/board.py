from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Board(Base):
    __tablename__ = "Board"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    board_name = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    category_ratio = Column(JSON, nullable=True)
    keyword = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    # user = relationship("User", back_populates="boards")
