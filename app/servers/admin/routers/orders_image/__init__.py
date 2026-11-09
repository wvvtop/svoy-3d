from fastapi import APIRouter
from . import read

orders_image_router = APIRouter(
    tags=["Роутер для фотографий заказов"],
    prefix="/orders/image"
)


orders_image_router.include_router(read.router)