from pydantic import BaseModel
from typing import List

class SaveKeywordsRequest(BaseModel):
    user_id: int
    category: str
    keywords: List[str]