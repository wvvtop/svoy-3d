from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.repositories.order.get_order import (
    get_deleted_order_by_id_and_user, 
    get_deleted_orders_by_user, 
    get_order_by_id_and_user,
    get_orders_by_user
)
from app.schemas.order import OrderInfo, DeletedOrder
from app.exceptions.order import (
    OrderNotFoundError,
    OrderNotDeletedError,
)


async def get_user_order(
    session: AsyncSession, 
    user: User,
    order_id: int
) -> OrderInfo:
    """Получение информации о заказе"""
    order = await get_order_by_id_and_user(session=session,user_id=user.id, order_id=order_id)
    if order is None:
        raise OrderNotFoundError()

    return OrderInfo.model_validate(order)

async def get_user_orders(
    session: AsyncSession, 
    user: User,
) -> list[OrderInfo]:
    """Получение информации о всех заказах"""
    orders = await get_orders_by_user(
        session=session,
        user_id=user.id, 
    )

    return [OrderInfo.model_validate(order) for order in orders]

async def get_deleted_order(
    session: AsyncSession, 
    user: User,
    order_id: int
) -> DeletedOrder:
    """Получение удаленного заказа пользователя"""

    order = await get_deleted_order_by_id_and_user(
        session=session,
        user_id=user.id,
        order_id=order_id,
    )

    if order is None:
        raise OrderNotDeletedError()

    return DeletedOrder.model_validate(order)

async def get_deleted_orders(
    session: AsyncSession, 
    user: User,
) -> list[DeletedOrder]:
    """Получение списка удаленных заказов пользователей"""

    orders = await get_deleted_orders_by_user(
        session=session,
        user_id=user.id,
    )

    return [DeletedOrder.model_validate(order) for order in orders]