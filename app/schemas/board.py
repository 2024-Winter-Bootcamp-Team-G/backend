from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")


class BoardBase(BaseModel):
    board_name: Optional[str]
    image_url: Optional[str]
    category_ratio: Optional[Dict]
    keyword: Optional[Dict]
    model_config = ConfigDict(from_attributes=True)


class BoardCreate(BoardBase):
    user_id: int
    redis_key: str  # Redis에서 데이터를 가져올 키
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))
    # created_at: Optional[datetime] = None



class BoardResponse(BoardBase):
    id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))
    model_config = ConfigDict(from_attributes=True)
