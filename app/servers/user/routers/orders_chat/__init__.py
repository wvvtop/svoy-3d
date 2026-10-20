from fastapi import APIRouter
from . import create, read, update

orders_chat_router = APIRouter(
    tags=["Роутер для чата заказов"],
    prefix="/orders"
)

orders_chat_router.include_router(create.router)
orders_chat_router.include_router(read.router)
orders_chat_router.include_router(update.router)