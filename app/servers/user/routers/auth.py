from fastapi import APIRouter


router = APIRouter(
    tags=["Роутер для авторизации"],
    prefix="/auth"
)