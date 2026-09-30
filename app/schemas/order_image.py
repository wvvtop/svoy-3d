from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrderImageUrl(BaseModel):
    id: int
    position: str
    preview_url: str
    compressed_url: str

    model_config = ConfigDict(from_attributes=True)