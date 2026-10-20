
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessageCreate(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Сообщение не может быть пустым")
        return value


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    author_id: int
    text: str
    created_at: datetime
    read_at: datetime | None


class ChatMessagePage(BaseModel):
    items: list[ChatMessageResponse]
    limit: int
    has_more: bool
    next_before_id: int | None


class UnreadOrderItem(BaseModel):
    order_id: int
    unread_count: int
    latest_message_at: datetime | None


class ChatUnreadResponse(BaseModel):
    total_unread: int
    orders: list[UnreadOrderItem]


class ChatReadResponse(BaseModel):
    order_id: int
    marked_count: int
