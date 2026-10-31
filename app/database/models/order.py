from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models import order_details


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

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    purged_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    photos: Mapped[list["OrderPhoto"]] = relationship(
        "OrderPhoto",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    generation_jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    models: Mapped[list["OrderModel"]] = relationship(
        "OrderModel",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    details: Mapped["OrderDetails | None"] = relationship(
        "OrderDetails",
        back_populates="order",
        uselist=False,                       # один-к-одному
        cascade="all, delete-orphan",        # удалили заказ — ушли детали
        single_parent=True,
    )

