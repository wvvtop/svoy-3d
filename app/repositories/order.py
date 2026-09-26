from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
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
    """Метод для получения активного заказа пользователя (Order)"""
    order = await session.execute(
        select(Order)
            .where(
                Order.id==order_id,
                Order.user_id==user_id,
                Order.deleted_at.is_(None)
            )
    )

    return order.scalar_one_or_none()

async def get_deleted_order_by_id_and_user(
    session: AsyncSession,
    user_id: int,
    order_id: int
) -> Order | None:
    """Получает удалённый заказ пользователя."""

    result = await session.execute(
        select(Order)
            .where(
                Order.id==order_id,
                Order.user_id==user_id,
                Order.deleted_at.is_not(None),
                Order.purged_at.is_(None)
            )
    )

    return result.scalar_one_or_none()

async def get_deleted_orders_by_user(
    session: AsyncSession,
    user_id: int
) -> list[Order]:
    """Возвращает заказы пользователя из корзины"""

    result = await session.execute(
        select(Order)
        .where(
            Order.user_id == user_id,
            Order.deleted_at.is_not(None),
            Order.purged_at.is_(None),
        )
        .order_by(Order.deleted_at.desc())
    )

    return list(result.scalars().all())


async def get_order_for_update(
    session: AsyncSession,
    user_id: int,
    order_id: int,
) -> Order | None:
    """Получает заказ и блокирует его до конца транзакции."""

    result = await session.execute(
        select(Order)
        .options(selectinload(Order.photos))
        .where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .with_for_update()
    )

    return result.scalar_one_or_none()
    