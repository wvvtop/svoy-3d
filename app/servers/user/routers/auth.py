from fastapi import APIRouter


router = APIRouter(
    tags=["Роутер для регистрации и авторизации"],
    prefix="/auth"
)

