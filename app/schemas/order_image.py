from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrderImageUrl(BaseModel):
    id: int
    position: str
    preview_url: str
    compressed_url: str

    review_status: str                 # "PENDING" | "APPROVED" | "REJECTED"
    review_error: str | None = None
    
    model_config = ConfigDict(from_attributes=True)