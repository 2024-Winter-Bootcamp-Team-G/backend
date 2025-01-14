from pydantic import BaseModel
from typing import List

class SelectedChannelsRequest(BaseModel):
    selected_channels: List[str]
