from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.schemas.chat import ChatMessagePage, ChatUnreadResponse
from app.servers.user.dependencies import CurrentUser
from app.services.chat import ChatService

router = APIRouter()


@router.get(
    "/chat/messages/unread",
    response_model=ChatUnreadResponse,
)
async def get_unread_messages(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Возвращает сводку непрочитанных сообщений по заказам для пользователя.

    Принимает:
        current_user — текущий пользователь (из CurrentUser).
        session (AsyncSession) — сессия БД (из get_session).
    Возвращает: ChatUnreadResponse — total_unread и список orders (UnreadOrderItem).
    """
    service = ChatService(session)

    return await service.get_unread(current_user)


@router.get(
    "/chat/messages/{order_id}",
    response_model=ChatMessagePage,
)
async def get_chat_messages(
    order_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(default=20, ge=1, le=100),
    before_id: int | None = Query(default=None, gt=0),
):
    """
    Возвращает страницу сообщений чата заказа для пользователя.

    Принимает:
        order_id (int) — ID заказа (path).
        current_user — текущий пользователь (из CurrentUser).
        session (AsyncSession) — сессия БД (из get_session).
        limit (int) — размер страницы, 1..100 (query, по умолчанию 20).
        before_id (int | None) — пагинация назад по id сообщения (query, > 0).
    Возвращает: ChatMessagePage — страница сообщений с limit, has_more и next_before_id.
    """
    service = ChatService(session)

    return await service.get_messages(
        order_id=order_id,
        actor=current_user,
        limit=limit,
        before_id=before_id,
    )
