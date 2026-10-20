from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.servers.user.dependencies import CurrentUser
from app.services.chat import ChatService


router = APIRouter()

@router.post(
    "/chat/messages/{order_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatMessageResponse
)
async def send_chat_message(
    order_id: int,
    payload: ChatMessageCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Отправляет сообщение в чат заказа от имени администратора.

    Принимает:
        order_id (int) — ID заказа (path).
        payload (ChatMessageCreate) — текст сообщения (JSON body).
        current_user — текущий пользователь (из CurrentUser).
        session (AsyncSession) — сессия БД (из зависимости get_session).
    Возвращает: ChatMessageResponse — созданное сообщение (201 Created).
    """
    service = ChatService(session)
    return await service.send_message(
        order_id=order_id,
        actor=current_user,
        text=payload.text,
    )



