from fastapi import APIRouter




router = APIRouter(
    tags=["Роутер для заказов"],
    prefix="/orders"
)

@router.get("/test")
async def test():
    return "ok"