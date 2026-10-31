from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.exceptions.order import OrderDetailsNotFoundError
from app.schemas.order_details import OrderDetailsRead
from app.servers.user.repositories.order_details.get import get_order_details_by_user_id_and_order_id


async def get_order_details(
    session: AsyncSession,
    user: User,
    order_id: int
) -> OrderDetailsRead:
    """Получение деталей заказа"""

    order_details = await get_order_details_by_user_id_and_order_id(
        session=session,
        user_id=user.id,
        order_id=order_id
    )

    if order_details is None:
        raise OrderDetailsNotFoundError()

    return OrderDetailsRead.model_validate(order_details)
