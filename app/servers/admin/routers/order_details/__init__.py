from fastapi import APIRouter
from . import read


router_order_details = APIRouter(
    tags=["Роутер для получения деталей заказа"],
    prefix="/orders/details"
)

router_order_details.include_router(read.router)