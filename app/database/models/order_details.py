from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OrderDetails(Base):
    """
    Класс с дополнительными данными по заказу
    """

    __tablename__ = "order_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    requests: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="details",
    )