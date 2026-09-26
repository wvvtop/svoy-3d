from fastapi import status

from app.exceptions.app_exception import AppError


class OrderError(AppError):
    """Базовый класс ошибок, связанных с заказами."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "order_error"
    message = "Order operation failed"


class OrderNotFoundError(OrderError):
    """Заказ не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "order_not_found"
    message = "Order not found"


class OrderAccessDeniedError(OrderError):
    """Заказ принадлежит другому пользователю."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "order_access_denied"
    message = "You do not have access to this order"


class OrderAlreadyExistsError(OrderError):
    """Заказ уже существует (конфликт уникальности)."""

    status_code = status.HTTP_409_CONFLICT
    code = "order_already_exists"
    message = "Order already exists"


class InvalidOrderStatusError(OrderError):
    """Недопустимый переход статуса заказа."""

    status_code = status.HTTP_409_CONFLICT
    code = "invalid_order_status"
    message = "Invalid order status transition"


class OrderCannotBeCancelledError(OrderError):
    """Заказ нельзя отменить в текущем статусе."""

    status_code = status.HTTP_409_CONFLICT
    code = "order_cannot_be_cancelled"
    message = "Order cannot be cancelled in its current status"


class OrderCreationError(OrderError):
    """Не удалось создать заказ."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "order_creation_failed"
    message = "Failed to create order"


class OrderAlreadyDeletedError(OrderError):
    """Заказ уже находится в корзине."""

    status_code = status.HTTP_409_CONFLICT
    code = "order_already_deleted"
    message = "Order is already deleted"


class OrderNotDeletedError(OrderError):
    """Заказ нельзя восстановить, потому что он не удалён."""

    status_code = status.HTTP_409_CONFLICT
    code = "order_not_deleted"
    message = "Order is not deleted"


class OrderAlreadyPurgedError(OrderError):
    """Данные заказа уже очищены."""

    status_code = status.HTTP_409_CONFLICT
    code = "order_already_purged"
    message = "Order data has already been purged"