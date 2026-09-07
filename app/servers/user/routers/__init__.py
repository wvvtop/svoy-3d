from fastapi import APIRouter
from .auth import router as auth_router
from .orders import router as order_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(order_router)