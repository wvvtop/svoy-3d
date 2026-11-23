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


from pydantic import BaseModel, Field


class OrderPhotoReviewUpdate(BaseModel):
    """Обновление статуса проверки изображения."""

    review_status: str = Field(
        ...,
        description="Статус проверки: PENDING | APPROVED | REJECTED",
    )
    review_error: str | None = Field(
        default=None,
        max_length=500,
        description="Причина отклонения (используется для REJECTED)",
    )