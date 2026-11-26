from typing import Any, Literal

from sqlalchemy.orm import selectinload
from app.servers.admin.types.pagination import CursorValue, OrderSortField, SortDirection
from sqlalchemy import and_, asc, desc, or_, select, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order import Order
from app.database.models.order_details import OrderDetails
from app.schemas.enums.order import OrderStatus

_SORT_COLUMNS = {
    "created_at": Order.created_at,
    "id": Order.id,
}


async def get_paginated_orders(
    session: AsyncSession,
    *,
    status: OrderStatus | None = None,
    limit: int = 20,
    sort_by: OrderSortField = "created_at",
    sort_dir: SortDirection = "desc",
    search: str | None = None,
    cursor_value: CursorValue | None = None,
    cursor_id: int | None = None,
) -> list[Order]:
    """
    Возвращает порцию заказов с поддержкой курсорной пагинации.

    Загружает связанные фотографии и детали заказов,
    поддерживает фильтрацию по статусу, поиск и сортировку.

    Запрашивает limit + 1 записей для определения наличия
    следующей страницы.

    Args:
        session: Асинхронная сессия базы данных.
        status: Статус заказов для фильтрации.
        limit: Максимальное количество заказов на странице.
        sort_by: Поле сортировки.
        sort_dir: Направление сортировки.
        search: Поисковая строка.
        cursor_value: Значение поля сортировки из курсора.
        cursor_id: ID заказа из курсора.

    Returns:
        list[Order]: Список заказов со связанными данными
            размером не более limit + 1.
    """
    sort_col = _SORT_COLUMNS[sort_by]
    is_desc = sort_dir == "desc"
    direction = desc if is_desc else asc

    # Загружаем фотографии и детали пакетными запросами.
    stmt = (
        select(Order)
        .options(
            selectinload(Order.photos),
            selectinload(Order.details),
        )
        .where(Order.deleted_at.is_(None))
    )

    # Фильтруем заказы по статусу.
    if status is not None:
        stmt = stmt.where(Order.status == status)

    # Нормализуем поисковую строку.
    term = (search or "").strip()

    if term:
        # Экранируем специальные символы LIKE.
        escaped_term = (
            term.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

        # Поиск по деталям без дублирования строк заказов.
        details_exists = (
            select(1)
            .where(
                OrderDetails.order_id == Order.id,
                OrderDetails.requests.ilike(
                    f"%{escaped_term}%",
                    escape="\\",
                ),
            )
            .exists()
        )

        conditions: list[ColumnElement[bool]] = [
            details_exists
        ]

        # Дополнительно ищем по ID для числовой строки.
        if term.isascii() and term.isdigit():
            order_id = int(term)

            if 0 < order_id <= 2**31 - 1:
                conditions.append(Order.id == order_id)

        stmt = stmt.where(or_(*conditions))

    # Применяем курсор предыдущей страницы.
    if cursor_value is not None and cursor_id is not None:
        if sort_by == "id":
            stmt = stmt.where(
                Order.id < cursor_id
                if is_desc
                else Order.id > cursor_id
            )

        elif is_desc:
            stmt = stmt.where(
                or_(
                    sort_col < cursor_value,
                    and_(
                        sort_col == cursor_value,
                        Order.id < cursor_id,
                    ),
                )
            )

        else:
            stmt = stmt.where(
                or_(
                    sort_col > cursor_value,
                    and_(
                        sort_col == cursor_value,
                        Order.id > cursor_id,
                    ),
                )
            )

    # ID обеспечивает детерминированную сортировку.
    if sort_by == "id":
        stmt = stmt.order_by(direction(Order.id))
    else:
        stmt = stmt.order_by(
            direction(sort_col),
            direction(Order.id),
        )

    # Дополнительная запись нужна для определения has_more.
    stmt = stmt.limit(limit + 1)

    result = await session.execute(stmt)

    return list(result.scalars().all())

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
            .where(Order.deleted_at.is_(None))
    )

    return list(orders.scalars().all())

async def get_all_new_active_orders(
    session: AsyncSession
) -> list[Order]:
    """Метод для получения активных, в статусе нового, заказов пользователей (Order), отправленных на доработку"""
    orders = await session.execute(
        select(Order)
            .where(Order.deleted_at.is_(None),
                   Order.status == OrderStatus.NEW)
    )

    return list(orders.scalars().all())
    

async def get_all_orders_on_revision(
    session: AsyncSession,
) -> list[Order]:
    """Метод для получения активных заказов пользователей (Order), отправленных на доработку"""
    orders = await session.execute(
        select(Order)
            .where(Order.deleted_at.is_(None),
                   Order.status == OrderStatus.REVISION)
    )

    return list(orders.scalars().all())