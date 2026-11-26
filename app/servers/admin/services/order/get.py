import binascii
from datetime import datetime
from typing import Any, Literal
import json
import base64
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.order import Order
from app.database.models.order_photo import OrderPhoto
from app.database.models.user import User
from app.exceptions.auth import UserNotFoundError
from app.exceptions.order import InvalidOrderCursorError, OrderNotFoundError
from app.repositories.user import get_user_by_id
from app.schemas.enums.order import OrderStatus
from app.schemas.order import AdminOrderListItem, AdminOrderPage, AdminOrderResponse, OrderInfo
from fastapi import status
from app.schemas.order_details import OrderRequestsRead
from app.schemas.order_image import OrderImageUrl
from app.servers.admin.repositories.order.get import (
    get_active_orders, 
    get_active_orders_by_user_id, 
    get_all_new_active_orders, 
    get_all_orders_on_revision, 
    get_order_by_order_id,
    get_paginated_orders
)
from app.servers.admin.types.pagination import CursorValue, OrderSortField, SortDirection
from app.services.storage import StorageService


def _encode_cursor(
    sort_by: OrderSortField,
    sort_dir: SortDirection,
    value: CursorValue,
    order_id: int,
) -> str:
    """
    Кодирует позицию последнего элемента страницы в строковый курсор.

    Курсор содержит поле и направление сортировки, значение
    поля сортировки и ID заказа для продолжения выборки.

    Args:
        sort_by: Поле сортировки.
        sort_dir: Направление сортировки.
        value: Значение поля сортировки последнего заказа.
        order_id: ID последнего заказа.

    Returns:
        str: Курсор, закодированный в URL-safe Base64.
    """
    # Преобразуем datetime в строку для сериализации в JSON.
    serialized_value = (
        value.isoformat()
        if isinstance(value, datetime)
        else value
    )

    payload = {
        "f": sort_by,
        "d": sort_dir,
        "v": serialized_value,
        "id": order_id,
    }

    raw = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    return base64.urlsafe_b64encode(raw).decode("ascii")


def _decode_cursor(
    cursor: str,
    expected_sort_by: OrderSortField,
    expected_sort_dir: SortDirection,
) -> tuple[CursorValue, int]:
    """
    Декодирует курсор и восстанавливает позицию для продолжения выборки.

    Проверяет структуру курсора, типы значений и соответствие
    параметров курсора текущей сортировке.

    Args:
        cursor: Закодированный курсор.
        expected_sort_by: Ожидаемое поле сортировки.
        expected_sort_dir: Ожидаемое направление сортировки.

    Returns:
        tuple[CursorValue, int]: Значение поля сортировки и ID заказа.

    Raises:
        InvalidOrderCursorError: Если курсор некорректен или
            не соответствует текущим параметрам сортировки.
    """
    try:
        # Декодируем Base64 со строгой проверкой формата.
        raw = base64.b64decode(
            cursor.encode("ascii"),
            altchars=b"-_",
            validate=True,
        )

        payload = json.loads(raw.decode("utf-8"))

        if not isinstance(payload, dict):
            raise InvalidOrderCursorError()

        # Проверяем соответствие параметров сортировки.
        if (
            payload.get("f") != expected_sort_by
            or payload.get("d") != expected_sort_dir
        ):
            raise InvalidOrderCursorError()

        value = payload["v"]
        order_id = payload["id"]

        # Строгая проверка ID без неявного преобразования типов.
        if type(order_id) is not int or order_id <= 0:
            raise InvalidOrderCursorError()

        # Восстанавливаем значение поля сортировки.
        if expected_sort_by == "created_at":
            if not isinstance(value, str):
                raise InvalidOrderCursorError()

            value = datetime.fromisoformat(value)

            # В модели Order используется DateTime без timezone.
            if value.tzinfo is not None:
                raise InvalidOrderCursorError()

        elif expected_sort_by == "id":
            if type(value) is not int or value != order_id:
                raise InvalidOrderCursorError()

        else:
            raise InvalidOrderCursorError()

        return value, order_id

    except (
        binascii.Error,
        ValueError,
        TypeError,
        KeyError,
        OverflowError,
    ) as exc:
        raise InvalidOrderCursorError() from exc


def build_order_image_url(
    photo: OrderPhoto,
    storage: StorageService,
) -> OrderImageUrl:
    """
    Формирует метаданные фотографии с подписанными URL.

    Использует готовый ORM-объект без дополнительных
    запросов к базе данных.

    Args:
        photo: ORM-объект фотографии заказа.
        storage: Сервис объектного хранилища.

    Returns:
        OrderImageUrl: Данные фотографии и ссылки на изображения.
    """
    return OrderImageUrl(
        id=photo.id,
        position=photo.position,
        preview_url=storage.get_presigned_url(
            photo.preview_object_key,
        ),
        compressed_url=storage.get_presigned_url(
            photo.compressed_object_key,
        ),
        review_status=photo.review_status,
        review_error=photo.review_error,
    )


def _build_order_list_item(
    order: Order,
    storage: StorageService,
) -> AdminOrderListItem:
    """
    Формирует расширенные данные заказа для отображения в списке.

    Использует предварительно загруженные фотографии и детали
    заказа без дополнительных запросов к базе данных.

    Args:
        order: ORM-объект заказа со связанными данными.
        storage: Сервис объектного хранилища.

    Returns:
        AdminOrderListItem: Данные карточки заказа.
    """
    # Формируем подписанные ссылки на фотографии.
    images = [
        build_order_image_url(photo, storage)
        for photo in order.photos
    ]

    # Детали заказа могут отсутствовать.
    requests = (
        OrderRequestsRead.model_validate(order.details)
        if order.details is not None
        else None
    )

    return AdminOrderListItem(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        created_at=order.created_at,
        images=images,
        requests=requests,
    )


def _build_order_list_items(
    orders: list[Order],
    storage: StorageService,
) -> list[AdminOrderListItem]:
    """
    Формирует расширенные данные для списка заказов.

    Предназначена для выполнения в отдельном потоке,
    поскольку клиент объектного хранилища синхронный.

    Все используемые ORM-атрибуты должны быть заранее
    загружены репозиторием.

    Args:
        orders: Список заказов со связанными данными.
        storage: Сервис объектного хранилища.

    Returns:
        list[AdminOrderListItem]: Список карточек заказов.
    """
    return [
        _build_order_list_item(order, storage)
        for order in orders
    ]


async def get_orders_page(
    session: AsyncSession,
    *,
    storage: StorageService,
    order_status: OrderStatus | None,
    limit: int,
    sort_by: OrderSortField,
    sort_dir: SortDirection,
    search: str | None,
    cursor: str | None,
) -> AdminOrderPage:
    """
    Получает расширенную страницу заказов с заданными параметрами.

    Декодирует курсор, запрашивает заказы со связанными
    фотографиями и деталями, формирует подписанные ссылки
    и информацию о следующей странице.

    Args:
        session: Асинхронная сессия базы данных.
        storage: Сервис объектного хранилища.
        order_status: Статус заказов для фильтрации.
        limit: Максимальное количество заказов на странице.
        sort_by: Поле сортировки.
        sort_dir: Направление сортировки.
        search: Поисковая строка.
        cursor: Курсор для получения следующей страницы.

    Returns:
        AdminOrderPage: Страница заказов с фотографиями,
            деталями и курсором следующей страницы.
    """
    cursor_value: CursorValue | None = None
    cursor_id: int | None = None

    # Восстанавливаем позицию предыдущей страницы.
    if cursor is not None:
        cursor_value, cursor_id = _decode_cursor(
            cursor=cursor,
            expected_sort_by=sort_by,
            expected_sort_dir=sort_dir,
        )

    # Загружаем заказы вместе с фотографиями и деталями.
    rows = await get_paginated_orders(
        session=session,
        status=order_status,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search=search,
        cursor_value=cursor_value,
        cursor_id=cursor_id,
    )

    # Дополнительная запись определяет наличие следующей страницы.
    has_more = len(rows) > limit
    page_items = rows[:limit]

    next_cursor: str | None = None

    # Формируем курсор по последнему возвращаемому заказу.
    if has_more and page_items:
        last_item = page_items[-1]

        next_cursor = _encode_cursor(
            sort_by=sort_by,
            sort_dir=sort_dir,
            value=getattr(last_item, sort_by),
            order_id=last_item.id,
        )

    # Формируем карточки вне event loop, поскольку MinIO синхронный.
    items = await run_in_threadpool(
        _build_order_list_items,
        page_items,
        storage,
    )

    return AdminOrderPage(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def get_new_active_orders(
    session: AsyncSession,
    *,
    storage: StorageService,
    limit: int = 20,
    sort_by: OrderSortField = "created_at",
    sort_dir: SortDirection = "desc",
    search: str | None = None,
    cursor: str | None = None,
) -> AdminOrderPage:
    """
    Получает страницу новых активных заказов.

    Поддерживает курсорную пагинацию, сортировку и поиск.
    Возвращает фотографии и детали каждого заказа.

    Args:
        session: Асинхронная сессия базы данных.
        storage: Сервис объектного хранилища.
        limit: Максимальное количество заказов на странице.
        sort_by: Поле сортировки.
        sort_dir: Направление сортировки.
        search: Поисковая строка.
        cursor: Курсор для получения следующей страницы.

    Returns:
        AdminOrderPage: Страница новых активных заказов.
    """
    return await get_orders_page(
        session=session,
        storage=storage,
        order_status=OrderStatus.NEW,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search=search,
        cursor=cursor,
    )


async def get_orders_on_revision(
    session: AsyncSession,
    *,
    storage: StorageService,
    limit: int = 20,
    sort_by: OrderSortField = "created_at",
    sort_dir: SortDirection = "desc",
    search: str | None = None,
    cursor: str | None = None,
) -> AdminOrderPage:
    """
    Получает страницу заказов, ожидающих доработки.

    Поддерживает курсорную пагинацию, сортировку и поиск.
    Возвращает фотографии и детали каждого заказа.

    Args:
        session: Асинхронная сессия базы данных.
        storage: Сервис объектного хранилища.
        limit: Максимальное количество заказов на странице.
        sort_by: Поле сортировки.
        sort_dir: Направление сортировки.
        search: Поисковая строка.
        cursor: Курсор для получения следующей страницы.

    Returns:
        AdminOrderPage: Страница заказов на доработке.
    """
    return await get_orders_page(
        session=session,
        storage=storage,
        order_status=OrderStatus.REVISION,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search=search,
        cursor=cursor,
    )


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
