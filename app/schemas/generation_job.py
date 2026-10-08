from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GenerationJobResponse(BaseModel):
    """Схема отдачи GenerationJob в API."""

    id: int
    order_id: int
    status: str
    provider_name: str
    external_request_id: str | None = None
    generation_mode: str
    attempts: int
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)