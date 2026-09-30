from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.database.dependencies import get_session
from app.database.models.user import User
from app.schemas.order import AdminOrderResponse, OrderInfo
from app.servers.admin.dependencies import CurrentAdmin
from app.servers.admin.services.order.get import get_order, get_orders, get_user_orders

router = APIRouter()


@router.get("/users/{user_id}", response_model=list[AdminOrderResponse])
async def get_user_order_info(
    current_user: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: int
):
    """Endpoint для получения информации о всех заказах пользователя"""
    return await get_user_orders(session=session, user_id=user_id)


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
