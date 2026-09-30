from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.schemas.order import OrderInfo, DeletedOrder
from app.servers.user.dependencies import CurrentUser
from app.database.dependencies import get_session
from app.servers.user.services.order.get_order import (
    get_deleted_order,
    get_deleted_orders, 
    get_user_order,
    get_user_orders, 
)

router = APIRouter()
    

@router.get("/deleted/{order_id}", response_model=DeletedOrder)
async def get_deleted(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Endpoint для получения информации об удаленном заказе"""
    return await get_deleted_order(
        session=session,
        user=current_user,
        order_id=order_id
    )

@router.get("/deleted", response_model=list[DeletedOrder])
async def get_deleted_user_orders(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Endpoint для получения информации всех удаленных заказов"""
    return await get_deleted_orders(
        session=session,
        user=current_user,
    )

@router.get("/{order_id}", response_model=OrderInfo)
async def get_order_info(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    order_id: int
):
    """Endpoint для получения информации о заказе"""
    return await get_user_order(session=session, user=current_user, order_id=order_id)

@router.get("/", response_model=list[OrderInfo])
async def get_orders_info(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Endpoint для получения информации о всех заказах""" 
    return await get_user_orders(session=session, user=current_user)


@router.get("/test")
async def test():
    return "ok"

@router.get("/test/auth")
async def test_auth(
    current_user: CurrentUser,
):
    return "auth ok"