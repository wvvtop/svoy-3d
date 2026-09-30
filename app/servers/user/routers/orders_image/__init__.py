from fastapi import APIRouter
from . import read, delete, upload

orders_image_router = APIRouter(
    tags=["Роутер для фотографий заказов"],
    prefix="/orders/image"
)


orders_image_router.include_router(read.router)
orders_image_router.include_router(delete.router)
orders_image_router.include_router(upload.router)

