from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrderDetailsRead(BaseModel):
    order_id: int
    requests: str | None = None
    
    model_config = ConfigDict(from_attributes=True)