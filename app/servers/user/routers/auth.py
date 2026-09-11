from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.schemas.user import UserResponse
from app.services.auth import login_user, register_user

router = APIRouter(
    tags=["Роутер для регистрации и авторизации"],
    prefix="/auth"
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def registration(
    data: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await register_user(session, data.email, data.password)

    return user

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
):
    access_token = await login_user(
        session=session,
        email=data.email,
        password=data.password,
    )

    return TokenResponse(
        access_token=access_token,
    )