from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderModelResponse(BaseModel):
    id: int
    order_id: int
    generation_job_id: int
    storage_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)