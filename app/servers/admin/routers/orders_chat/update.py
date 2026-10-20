from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_session
from app.servers.admin.dependencies import CurrentAdmin
from app.services.chat import ChatService


router = APIRouter()

@router.patch(
    "/chat/messages/read/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def mark_chat_as_read(
    order_id: int,
    current_admin: CurrentAdmin,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Отмечает как прочитанные все входящие сообщения чата заказа.

    Принимает:
        order_id (int) — ID заказа (path).
        current_admin — текущий администратор (из зависимости CurrentAdmin).
        session (AsyncSession) — сессия БД (из get_session).
    Возвращает: ChatReadResponse — order_id и marked_count (сколько сообщений отмечено; 0, если диалога нет).
    """
    service = ChatService(session)
    await service.mark_read(
        order_id=order_id,
        actor=current_admin,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)