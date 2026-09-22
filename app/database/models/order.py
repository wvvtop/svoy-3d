from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"
    """Таблица order с заказами"""
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False,index=True)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="NEW",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    photos: Mapped[list["OrderPhoto"]] = relationship(
        "OrderPhoto",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

