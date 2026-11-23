from fastapi import APIRouter
from . import read, update

orders_image_router = APIRouter(
    tags=["Роутер для фотографий заказов"],
    prefix="/orders"
)


orders_image_router.include_router(read.router)
orders_image_router.include_router(update.router)