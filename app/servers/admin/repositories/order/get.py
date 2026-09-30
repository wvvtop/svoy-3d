from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order import Order


async def get_order_by_order_id(
    session: AsyncSession,
    order_id: int,
) -> Order | None:
    """Метод для получения активного заказа пользователя (Order)"""
    order = await session.execute(
        select(Order)
            .where(
                Order.id==order_id,
                Order.deleted_at.is_(None)
            )
    )

    return order.scalar_one_or_none()

async def get_active_orders_by_user_id(
    session: AsyncSession,
    user_id: int
) -> list[Order]:
    """Метод для получения активных заказов пользователя (Order)"""
    orders = await session.execute(
        select(Order)
            .where(
                Order.user_id==user_id,
                Order.deleted_at.is_(None)
            )
    )

    return list(orders.scalars().all())


async def get_active_orders(
    session: AsyncSession,
) -> list[Order]:
    """Метод для получения активных заказов пользователей (Order)"""
    orders = await session.execute(
        select(Order)
    )

    return list(orders.scalars().all())