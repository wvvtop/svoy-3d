from fastapi import APIRouter
from . import auth
from . import orders
router = APIRouter()

router.include_router(auth.router)
router.include_router(orders.orders_router)
# orders_router.include_router(create.router)
# orders_router.include_router(delete.router)
# orders_router.include_router(read.router)
# orders_router.include_router(restore.router)