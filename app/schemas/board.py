from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict
from datetime import datetime


class BoardBase(BaseModel):
    board_name: Optional[str]
    image_url: Optional[str]
    category_ratio: Optional[Dict]
    keyword: Optional[Dict]
    model_config = ConfigDict(from_attributes=True)


class BoardCreate(BoardBase):
    # user_id: int
    created_at: datetime = Field(default_factory=datetime.now)  # 기본값 설정
    pass

class BoardResponse(BoardBase):
    id: int
    created_at: Optional[datetime]
