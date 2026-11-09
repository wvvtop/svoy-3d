from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.order_details import OrderDetailsNotFound
from app.schemas import order_details
from app.schemas.order_details import OrderRequestsRead
from app.servers.admin.repositories.order_details.get import get_order_details_by_order_id


async def get_order_requests(
    session: AsyncSession,
    order_id: int
) -> OrderRequestsRead:
    """Сервис получения запросов к заказу"""

    details = await get_order_details_by_order_id(session=session, order_id=order_id)

    if details is None:
        raise OrderDetailsNotFound()

    return OrderRequestsRead.model_validate(details)
