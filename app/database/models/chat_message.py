from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    __table_args__ = (
        Index(
            "ix_chat_messages_conversation_id_id",
            "conversation_id",
            "id",
        ),
        Index(
            "ix_chat_messages_conversation_read_at",
            "conversation_id",
            "read_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chat_conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    conversation: Mapped["ChatConversation"] = relationship(
        back_populates="messages",
    )

    author: Mapped["User"] = relationship()