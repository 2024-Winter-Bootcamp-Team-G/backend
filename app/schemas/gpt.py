from pydantic import BaseModel
from typing import List, Dict


class GPTRequest(BaseModel):
    video_list: List[str]


class GPTResponse(BaseModel):
    categories: Dict[str, float]
    keywords: Dict[str, List[str]]
