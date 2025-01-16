from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, List
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")


class BoardBase(BaseModel):
    board_name: Optional[str]
    image_url: Optional[str]
    category_ratio: Optional[Dict]
    keywords: Optional[List[str]]
    category: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class BoardCreate(BoardBase):
    redis_key: Optional[str] = None  # Redis에서 데이터를 가져올 키
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))


class BoardResponse(BoardBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
