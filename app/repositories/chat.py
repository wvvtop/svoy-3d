from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.database.models.chat_conversation import ChatConversation
from app.database.models.chat_message import ChatMessage
from app.database.models.order import Order
from app.database.models.user import User
from app.exceptions.chat import ChatConversationCreateFailedError


class ChatRepository:
    def __init__(self, session: AsyncSession):
        """
        Инициализирует репозиторий чата.

        Принимает: session (AsyncSession) — асинхронная сессия БД.
        Возвращает: None.
        """
        self.session = session

    def _incoming_role(self, reader: User) -> str:
        """
        Определяет роль авторов входящих (непрочитанных) сообщений для читателя.

        Принимает: reader (User) — пользователь, читающий чат.
        Возвращает: str — 'USER' для администратора, иначе 'ADMIN'.
        """
        return "USER" if reader.role == "ADMIN" else "ADMIN"

    async def get_conversation(self, order_id: int) -> ChatConversation | None:
        """
        Возвращает диалог чата по ID заказа.

        Принимает: order_id (int) — ID заказа.
        Возвращает: ChatConversation | None — диалог или None, если не существует.
        """
        result = await self.session.execute(
            select(ChatConversation).where(
                ChatConversation.order_id == order_id
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_conversation(self, order_id: int) -> ChatConversation:
        """
        Возвращает существующий диалог по заказу или создаёт новый
        (безопасно при одновременных запросах через ON CONFLICT DO NOTHING).

        Принимает: order_id (int) — ID заказа.
        Возвращает: ChatConversation — найденный или созданный диалог.
        Исключения: ChatConversationCreateFailedError — если диалог не удалось создать.
        """
        # PostgreSQL: безопасно при одновременных запросах.
        statement = (
            insert(ChatConversation)
            .values(order_id=order_id)
            .on_conflict_do_nothing(index_elements=[ChatConversation.order_id])
        )

        await self.session.execute(statement)

        conversation = await self.get_conversation(order_id)

        if conversation is None:
            raise ChatConversationCreateFailedError()

        return conversation

    async def get_messages(
        self,
        conversation_id: int,
        limit: int,
        before_id: int | None = None
    ) -> tuple[list[ChatMessage], bool]:
        """
        Возвращает страницу сообщений диалога (от старых к новым) и флаг наличия более старых.

        Принимает:
            conversation_id (int) — ID диалога.
            limit (int) — максимальное количество сообщений в выдаче.
            before_id (int | None) — вернуть сообщения с id строго меньше указанного (пагинация назад).
        Возвращает: tuple[list[ChatMessage], bool] — сообщения в хронологическом порядке и признак has_more.
        """
        statement = select(ChatMessage).where(
            ChatMessage.conversation_id == conversation_id
        )

        if before_id is not None:
            statement = statement.where(
                ChatMessage.id < before_id
            )

        statement = (
            statement
                .order_by(ChatMessage.id.desc())
                .limit(limit + 1)
        )

        result = await self.session.execute(statement)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        rows = rows[:limit]

        rows.reverse()

        return rows, has_more

    async def create_message(
        self, 
        conversation_id: int,
        author_id: int,
        text: str
    ) -> ChatMessage:
        """
        Создаёт сообщение в диалоге и бампает updated_at у диалога (в одной транзакции).

        Принимает:
            conversation_id (int) — ID диалога.
            author_id (int) — ID автора сообщения.
            text (str) — текст сообщения.
        Возвращает: ChatMessage — сохранённое сообщение с заполненными id и created_at (после flush).
        """
        message = ChatMessage(
            conversation_id=conversation_id,
            author_id=author_id,
            text=text
        )

        self.session.add(message)

        await self.session.flush()

        await self.session.execute(
            update(ChatConversation)
            .where(ChatConversation.id == conversation_id)
            .values(updated_at=func.now())
        )

        return message

    async def mark_read(
        self,
        conversation_id: int,
        reader: User
    ) -> int:
        """
        Проставляет read_at для всех непрочитанных сообщений «входящей» стороны.

        Принимает:
            conversation_id (int) — ID диалога.
            reader (User) — пользователь, читающий чат.
        Возвращает: int — количество отмеченных сообщений.
        """
        # Администратор читает сообщения пользователей.
        # Пользователь читает сообщения администраторов.
        incoming_role = self._incoming_role(reader)

        incoming_authors = select(User.id).where(
            User.role == incoming_role
        )

        statement = (
            update(ChatMessage)
            .where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.author_id.in_(incoming_authors),
                ChatMessage.read_at.is_(None),
            )
            .values(read_at=func.now())
            .returning(ChatMessage.id)
        )

        result = await self.session.execute(statement)
        return len(result.scalars().all())

    async def get_unread_by_order(
        self,
        reader: User,
    ) -> list[dict]:
        """
        Возвращает агрегированную статистику непрочитанных сообщений по заказам.

        Принимает: reader (User) — пользователь, для которого считается статистика.
        Возвращает: list[dict] — элементы с ключами:
            order_id (int), unread_count (int), latest_message_at (datetime | None).
        """
        incoming_role = self._incoming_role(reader)
        
        statement = (
            select(
                Order.id.label("order_id"),
                func.count(ChatMessage.id).label("unread_count"),
                func.max(ChatMessage.created_at).label(
                    "latest_message_at"
                ),
            )
            .join(
                ChatConversation,
                ChatConversation.order_id == Order.id,
            )
            .join(
                ChatMessage,
                ChatMessage.conversation_id == ChatConversation.id,
            )
            .join(User, User.id == ChatMessage.author_id)
            .where(
                User.role == incoming_role,
                ChatMessage.read_at.is_(None),
            )
            .group_by(Order.id)
            .order_by(func.max(ChatMessage.created_at).desc())
        )

        # Администратор видит все заказы.
        # Обычный пользователь — только собственные.
        if reader.role != "ADMIN":
            statement = statement.where(
                Order.user_id == reader.id
            )

        result = await self.session.execute(statement)

        return [
            {
                "order_id": row.order_id,
                "unread_count": row.unread_count,
                "latest_message_at": row.latest_message_at,
            }
            for row in result.all()
        ]
