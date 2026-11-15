from fastapi import APIRouter
from . import read, update

orders_router = APIRouter(
    tags=["Роутер для работы с заказами клиентов"],
    prefix="/orders"
)

orders_router.include_router(read.router)
orders_router.include_router(update.router)