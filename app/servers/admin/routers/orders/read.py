from typing import Annotated, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, Request
from app.database.dependencies import get_session
from app.database.models.user import User
from app.schemas.order import AdminOrderPage, AdminOrderResponse, OrderInfo
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.services.order.get import (
    get_new_active_orders, 
    get_order, get_orders, 
    get_orders_on_revision, 
    get_user_orders
)
from app.servers.admin.types.pagination import OrderSortField, SortDirection


router = APIRouter()


@router.get("/users/{user_id}", response_model=list[AdminOrderResponse])
async def get_user_order_info(
    current_user: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: int
):
    """Endpoint для получения информации о всех заказах пользователя"""
    return await get_user_orders(session=session, user_id=user_id)

@router.get("/revision", response_model=AdminOrderPage)
async def get_revision_orders(
    current_user: CurrentAdmin,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(
        default=None,
        min_length=1,
        max_length=2048,
    ),
    sort_by: OrderSortField = Query(default="created_at"),
    sort_dir: SortDirection = Query(default="desc"),
    search: str | None = Query(default=None, max_length=200),
):
    """
    Получает страницу заказов, ожидающих доработки.

    Поддерживает курсорную пагинацию, сортировку и поиск.
    """

    storage = request.app.state.photo_storage

    return await get_orders_on_revision(
        session=session,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search=search,
        cursor=cursor,
        storage=storage
    )


@router.get("/new", response_model=AdminOrderPage)
async def get_active_new_orders_info(
    current_user: CurrentAdmin,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(
        default=None,
        min_length=1,
        max_length=2048,
    ),
    sort_by: OrderSortField = Query(default="created_at"),
    sort_dir: SortDirection = Query(default="desc"),
    search: str | None = Query(default=None, max_length=200),
):
    """
    Получает страницу новых активных заказов.

    Поддерживает курсорную пагинацию, сортировку и поиск.
    """

    storage = request.app.state.photo_storage

    return await get_new_active_orders(
        session=session,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search=search,
        cursor=cursor,
        storage=storage
    )

@router.get("/{order_id}", response_model=AdminOrderResponse)
async def get_order_info(
    current_user: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Endpoint для получения информации о конкретном заказе"""
    return await get_order(session=session, order_id=order_id)

@router.get("/", response_model=list[AdminOrderResponse])
async def get_orders_info(
    current_user: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Endpoint для получения информации о всех заказах""" 

    return await get_orders(session=session)
