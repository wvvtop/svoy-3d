from fastapi import APIRouter
from . import read, update


order_details_router = APIRouter(
    prefix="/orders"
)

order_details_router.include_router(read.router)
order_details_router.include_router(update.router)
