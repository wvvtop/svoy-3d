from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order_details import OrderRequestsRead
from app.schemas.order_image import OrderImageUrl


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


class AdminOrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class AdminOrderListItem(AdminOrderResponse):
    """
    Расширенная информация о заказе для отображения в списке.

    Содержит основную информацию, фотографии и пожелания
    пользователя к заказу.
    """

    images: list[OrderImageUrl] = Field(default_factory=list)
    requests: OrderRequestsRead | None = None

class AdminOrderPage(BaseModel):
    items: list[AdminOrderListItem]
    next_cursor: str | None = None
    has_more: bool = False