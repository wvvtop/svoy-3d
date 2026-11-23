from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class OrderRequestsUpdate(BaseModel):
    requests: str = Field(default="", max_length=5000)

class OrderDetailsRead(BaseModel):
    order_id: int
    requests: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class OrderRequestsRead(BaseModel):
    order_id: int
    requests: str | None = None
    
    model_config = ConfigDict(from_attributes=True)