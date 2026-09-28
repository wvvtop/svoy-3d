from fastapi import APIRouter
from .auth import router as auth_router
from .orders import orders_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(orders_router)