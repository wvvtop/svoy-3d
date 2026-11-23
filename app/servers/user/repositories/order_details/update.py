from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.order_details import OrderDetails


async def update_order_details_requests(
    session: AsyncSession,
    details: OrderDetails,
    requests: str,
) -> OrderDetails:
    details.requests = requests
    await session.flush()   # отправляем UPDATE в БД, но не коммитим
    return details