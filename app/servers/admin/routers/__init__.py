from fastapi import APIRouter
from . import auth
from . import orders
from . import models
from . import orders_chat

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(orders.orders_router)
router.include_router(models.router)
router.include_router(orders_chat.orders_chat_router)
# orders_router.include_router(create.router)
# orders_router.include_router(delete.router)
# orders_router.include_router(read.router)
# orders_router.include_router(restore.router)