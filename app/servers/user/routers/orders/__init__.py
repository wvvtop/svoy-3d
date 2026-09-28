from fastapi import APIRouter
from . import create, delete, read, restore

orders_router = APIRouter(
    tags=["Роутер для заказов"],
    prefix="/orders"
)

orders_router.include_router(create.router)
orders_router.include_router(delete.router)
orders_router.include_router(read.router)
orders_router.include_router(restore.router)