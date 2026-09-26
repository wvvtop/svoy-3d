from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrderInfo(BaseModel):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DeletedOrder(BaseModel):
    id: int
    status: str
    created_at: datetime
    deleted_at: datetime

    model_config = ConfigDict(from_attributes=True)