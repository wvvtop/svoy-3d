from fastapi import status

from app.exceptions.app_exception import AppError


class OrderImageError(AppError):
    """Базовый класс ошибок, связанных с заказами."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "order_image_error"
    message = "Order image operation failed"

class OrderImageNotFoundError(OrderImageError):
    """Изображение не найдено"""

    status_code = status.HTTP_404_NOT_FOUND
    code = "order_image_not_found"
    message = "Order image not found"

class OrderImageInvalidPosition(OrderImageError):
    """Позиция фото некоректна"""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "order_image_invalid_position"
    message = "Invalid photo position"

class OrderImageAlreadyExistsError(OrderImageError):
    status_code = 409
    detail = "An image with this position already exists."
    