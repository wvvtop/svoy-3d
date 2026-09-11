from typing import Annotated

from fastapi import APIRouter, Depends

from app.database.models.user import User
from app.servers.user.dependencies import get_current_user




router = APIRouter(
    tags=["Роутер для заказов"],
    prefix="/orders"
)

@router.get("/test")
async def test():
    return "ok"

@router.get("/test/auth")
async def test_auth(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return "auth ok"
