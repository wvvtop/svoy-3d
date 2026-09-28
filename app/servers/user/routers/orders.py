from typing import Annotated
from urllib import request
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.schemas.order import OrderInfo, DeletedOrder
from app.servers.user.dependencies import get_current_user
from app.database.dependencies import get_session
from app.schemas.enums.order import PhotoPosition
from app.services.order.delete_order import (
    delete_user_order,
    purge_user_order, 
    restore_user_order
)
from app.services.order.create_order import create_order_with_photos
from app.services.order.get_order import (
    get_deleted_order,
    get_deleted_orders, 
    get_user_order,
    get_user_orders, 
)

router = APIRouter(
    tags=["Роутер для заказов"],
    prefix="/orders"
)




