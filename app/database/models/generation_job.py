from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GenerationJobStatus(str, Enum):
    """Статусы задачи генерации."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class GenerationMode(str, Enum):
    """Режимы генерации (multi_view | single_view)."""

    MULTI_VIEW = "multi_view"
    SINGLE_VIEW = "single_view"


class GenerationJob(Base):
    """
    Задача генерации 3D-модели.

    Используется как запись очереди: worker забирает PENDING
    и переводит в PROCESSING → SUCCESS/FAILED.
    """

    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=GenerationJobStatus.PENDING.value,
        index=True,
    )

    # ── провайдер ─────────────────────────────────────────
    provider_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="genapi",
    )

    external_request_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    generation_mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=GenerationMode.MULTI_VIEW.value,
    )

    # ── метаданные ────────────────────────────────────────
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="generation_jobs",
    )

    model: Mapped["OrderModel | None"] = relationship(
        "OrderModel",
        back_populates="generation_job",
        uselist=False,
    )
