from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.exceptions.order import OrderNotFoundError
from app.servers.admin.repositories.order.get import get_order_by_order_id
from app.servers.admin.repositories.order.update import (
    mark_order_for_revision_by_order_id, 
    revert_order_from_revision_by_order_id
)


async def revert_order_from_revision(
    session: AsyncSession,
    order_id: int
):
    """Сервис возвращает заказ из доработки""" 

    order = await get_order_by_order_id(
        session=session,
        order_id=order_id
    )

    if order is None:
        raise OrderNotFoundError()

    await revert_order_from_revision_by_order_id(
        session=session,
        order=order
    )

    await session.commit()
   

async def mark_order_for_revision(
    session: AsyncSession,
    order_id: int
):
    """Сервис отмечает заказ статусом на доработку"""

    order = await get_order_by_order_id(
        session=session,
        order_id=order_id
    )

    if order is None:
        raise OrderNotFoundError()

    await mark_order_for_revision_by_order_id(
        session=session,
        order=order
    )

    await session.commit()
