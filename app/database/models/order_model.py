from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OrderModel(Base):
    """
    Готовая 3D-модель, привязанная к заказу.

    Один Order может иметь несколько OrderModel
    (несколько генераций).
    """

    __tablename__ = "order_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generation_job_id: Mapped[int] = mapped_column(
        ForeignKey("generation_jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="models",
    )

    generation_job: Mapped["GenerationJob"] = relationship(
        "GenerationJob",
        back_populates="model",
    )