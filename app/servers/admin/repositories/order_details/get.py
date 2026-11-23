from sqlalchemy import select

from app.database.models.order_details import OrderDetails
from app.schemas.order_details import OrderRequestsRead
from sqlalchemy.ext.asyncio import AsyncSession


async def get_order_details_by_order_id(
    session: AsyncSession,
    order_id: int
) -> OrderDetails | None:
    """Получение деталей заказа по id заказа"""

    result = await session.execute(
        select(OrderDetails).where(
            OrderDetails.order_id == order_id
        )
    )

    return result.scalar_one_or_none()
