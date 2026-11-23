from fastapi import APIRouter
from . import auth
from . import orders
from . import models
from . import orders_chat
from . import orders_image
from . import order_details

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(orders.orders_router)
router.include_router(models.router)
router.include_router(orders_chat.orders_chat_router)
router.include_router(orders_image.orders_image_router)
router.include_router(order_details.router_order_details)
# orders_router.include_router(create.router)
# orders_router.include_router(delete.router)
# orders_router.include_router(read.router)
# orders_router.include_router(restore.router)