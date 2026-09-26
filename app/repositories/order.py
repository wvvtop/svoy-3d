from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.enums.order import OrderStatus
from app.database.models.order import Order


async def create_order(
    session: AsyncSession,
    user_id: int
) -> Order:
    order = Order(user_id=user_id, status=OrderStatus.NEW)

    session.add(order)

    # flush отправляет INSERT в БД,
    # но НЕ завершает transaction.
    await session.flush()

    return order


async def get_order_by_id_and_user(
    session: AsyncSession,
    user_id: int,
    order_id: int
) -> Order | None:
    """Метод для получения Order"""
    order = await session.execute(
        select(Order)
            .where(Order.id==order_id,
                   Order.user_id==user_id)
    )

    return order.scalar_one_or_none()
    