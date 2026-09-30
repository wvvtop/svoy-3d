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