from pydantic import BaseModel, ConfigDict, Field, root_validator
from typing import Optional, Dict, List
import json
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")


class BoardBase(BaseModel):
    board_name: Optional[str]
    image_url: Optional[str]
    category_ratio: Optional[List[int]]
    keywords: Optional[Dict[str, List[str]]]

    model_config = ConfigDict(from_attributes=True)


class BoardCreate(BoardBase):
    redis_key: Optional[str] = None


class BoardResponse(BoardBase):
    id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))

    @root_validator(pre=True)
    def validate_fields(cls, values):
        if isinstance(values.get("category_ratio"), str):
            values["category_ratio"] = json.loads(values["category_ratio"])
        if isinstance(values.get("keywords"), str):
            values["keywords"] = json.loads(values["keywords"])
        return values

    model_config = ConfigDict(from_attributes=True)