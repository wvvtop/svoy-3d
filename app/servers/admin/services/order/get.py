from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.exceptions.auth import UserNotFoundError
from app.exceptions.order import OrderNotFoundError
from app.repositories.user import get_user_by_id
from app.schemas.order import AdminOrderResponse, OrderInfo
from app.servers.admin.repositories.order.get import get_active_orders, get_active_orders_by_user_id, get_order_by_order_id


async def get_order(
    session: AsyncSession, 
    order_id: int
) -> AdminOrderResponse:
    """Получение информации о заказе конкретного пользователя"""

    order = await get_order_by_order_id(
        session=session,
        order_id=order_id
    )
    if order is None:
        raise OrderNotFoundError()

    return AdminOrderResponse.model_validate(order)


async def get_orders(
    session: AsyncSession, 
) -> list[AdminOrderResponse]:
    """Получение информации о всех заказах пользователей"""

    orders = await get_active_orders(session=session)

    return [AdminOrderResponse.model_validate(order) for order in orders]

async def get_user_orders(
    session: AsyncSession, 
    user_id: int,
) -> list[AdminOrderResponse]:
    """Получение информации о всех заказах пользователя"""
    user = await get_user_by_id(session=session, user_id=user_id)

    if user is None:
        raise UserNotFoundError()

    orders = await get_active_orders_by_user_id(
        session=session,
        user_id=user.id, 
    )

    return [AdminOrderResponse.model_validate(order) for order in orders]