from fastapi import status
from app.exceptions.app_exception import AppError


class ChatError(AppError):
    """Базовая ошибка чата."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "chat_error"
    message = "Chat operation failed"

class ChatConversationCreateFailedError(ChatError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "chat_conversation_create_failed"
    message = "Failed to create chat conversation"

class ChatConversationNotFoundError(ChatError):
    """Диалог не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "chat_conversation_not_found"
    message = "Chat conversation not found"


class ChatMessageNotFoundError(ChatError):
    """Сообщение не найдено."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "chat_message_not_found"
    message = "Chat message not found"


class ChatOrderNotFoundError(ChatError):
    """Заказ для чата не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "chat_order_not_found"
    message = "Order not found"


class ChatAccessDeniedError(ChatError):
    """Нет доступа к чату заказа."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "chat_access_denied"
    message = "Access to this chat is denied"


class ChatMessageEmptyError(ChatError):
    """Сообщение пустое после удаления пробелов."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "chat_message_empty"
    message = "Chat message cannot be empty"


class ChatMessageTooLongError(ChatError):
    """Сообщение превышает допустимую длину."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "chat_message_too_long"
    message = "Chat message exceeds the maximum allowed length"


class ChatInvalidPaginationError(ChatError):
    """Некорректные параметры пагинации."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "chat_invalid_pagination"
    message = "Invalid chat pagination parameters"


class ChatAdminRequiredError(ChatError):
    """Операция доступна только администратору."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "chat_admin_required"
    message = "Administrator privileges are required"
