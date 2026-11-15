from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.order import Order
from app.schemas.enums.order import OrderStatus


async def mark_order_for_revision_by_order_id(
    session: AsyncSession,
    order: Order   
) -> Order:
    """Изменение статуса заказа на revision"""
    
    order.status = OrderStatus.REVISION
    await session.flush()
    return order

async def revert_order_from_revision_by_order_id(
    session: AsyncSession,
    order: Order   
) -> Order:
    """Изменение статуса заказа в статус нового"""
    
    order.status = OrderStatus.NEW
    await session.flush()
    return order

