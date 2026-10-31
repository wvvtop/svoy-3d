from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.order import Order
from app.database.models.order_details import OrderDetails


async def get_order_details_by_user_id_and_order_id(
    session: AsyncSession,
    user_id: int,
    order_id: int,
) -> OrderDetails | None:
    """Получение деталей заказа по user id и order id"""

    order_details = await session.execute(
        select(OrderDetails)
            .join(Order, Order.id == OrderDetails.order_id)
            .where(
                OrderDetails.order_id==order_id,
                Order.user_id == user_id,
            )
    )

    return order_details.scalar_one_or_none()