
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.order import Order
from app.database.models.user import User
from app.exceptions.chat import (
    ChatOrderNotFoundError,
)
from app.repositories.chat import ChatRepository
from app.schemas.chat import (
    ChatMessagePage,
    ChatMessageResponse,
    ChatUnreadResponse,
    UnreadOrderItem,
)


class ChatService:
    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис чата и его репозиторий.

        Принимает: session (AsyncSession) — асинхронная сессия БД.
        Возвращает: None.
        """
        self.session = session
        self.repository = ChatRepository(session)

    async def _check_order_access(
        self,
        order_id: int,
        actor: User,
    ) -> Order:
        """
        Проверяет существование заказа и права доступа к нему.

        Принимает:
            order_id (int) — ID заказа.
            actor (User) — пользователь, запрашивающий доступ.
        Возвращает: Order — заказ, если доступ разрешён.
        Исключения: ChatOrderNotFoundError — если заказ не найден или недоступен пользователю
            (для не-админа чужой заказ маскируется под «не найден»).
        """
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if order is None:
            raise ChatOrderNotFoundError()

        if actor.role == "ADMIN":
            return order

        if order.user_id != actor.id:
            # Не раскрываем факт существования чужого заказа.
            raise ChatOrderNotFoundError()

        return order

    async def get_messages(
        self,
        order_id: int,
        actor: User,
        limit: int = 20,
        before_id: int | None = None,
    ) -> ChatMessagePage:
        """
        Возвращает страницу сообщений чата по заказу для указанного пользователя.

        Принимает:
            order_id (int) — ID заказа.
            actor (User) — пользователь, запрашивающий сообщения.
            limit (int) — размер страницы (по умолчанию 20).
            before_id (int | None) — пагинация назад: id, строго меньше которого отдавать сообщения.
        Возвращает: ChatMessagePage — страница сообщений с limit, has_more и next_before_id.
            Если диалога ещё нет — пустая страница с has_more=False.
        Исключения: ChatOrderNotFoundError — если заказ не найден или недоступен.
        """
        await self._check_order_access(order_id, actor)

        conversation = await self.repository.get_conversation(
            order_id
        )

        if conversation is None:
            return ChatMessagePage(
                items=[],
                limit=limit,
                has_more=False,
                next_before_id=None,
            )

        messages, has_more = await self.repository.get_messages(
            conversation_id=conversation.id,
            limit=limit,
            before_id=before_id,
        )

        return ChatMessagePage(
            items=[
                ChatMessageResponse.model_validate(message)
                for message in messages
            ],
            limit=limit,
            has_more=has_more,
            next_before_id=(
                messages[0].id if has_more and messages else None
            ),
        )

    async def send_message(
        self,
        order_id: int,
        actor: User,
        text: str,
    ) -> ChatMessageResponse:
        """
        Создаёт сообщение в чате заказа от имени пользователя.

        Принимает:
            order_id (int) — ID заказа.
            actor (User) — автор сообщения.
            text (str) — текст сообщения (уже провалидирован схемой).
        Возвращает: ChatMessageResponse — созданное сообщение.
        Исключения: ChatOrderNotFoundError — если заказ не найден или недоступен;
            ChatConversationCreateFailedError — если не удалось создать диалог.
        """
        try:
            order = await self._check_order_access(order_id, actor)

            conversation = await self.repository.get_or_create_conversation(
                order_id=order.id,
            )

            message = await self.repository.create_message(
                conversation_id=conversation.id,
                author_id=actor.id,
                text=text,
            )

            response = ChatMessageResponse.model_validate(message)

            await self.session.commit()

            return response
        except Exception:
            await self.session.rollback()
            raise

    async def mark_read(
        self,
        order_id: int,
        actor: User,
    ) -> None:
        """
        Отмечает как прочитанные все входящие сообщения чата заказа.

        Принимает:
            order_id (int) — ID заказа.
            actor (User) — пользователь, читающий чат.
        Возвращает: None.
        Исключения: ChatOrderNotFoundError — если заказ не найден или недоступен.
        """
        try:
            order = await self._check_order_access(order_id, actor)

            conversation = await self.repository.get_conversation(
                order_id=order.id,
            )

            if conversation is None:
                return

            await self.repository.mark_read(
                conversation_id=conversation.id,
                reader=actor,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def get_unread(
        self,
        actor: User,
    ) -> ChatUnreadResponse:
        rows = await self.repository.get_unread_by_order(actor)

        orders = [
            UnreadOrderItem(**row)
            for row in rows
        ]

        return ChatUnreadResponse(
            total_unread=sum(item.unread_count for item in orders),
            orders=orders,
        )
