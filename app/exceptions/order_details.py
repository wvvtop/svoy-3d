from fastapi import status

from app.exceptions.app_exception import AppError


class OrderDetailsError(AppError):
    """Базовый класс ошибок, связанных с деталями заказа."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "order_details_error"
    message = "Order details operation failed"

class OrderDetailsNotFound(OrderDetailsError):
    """Детали заказа не найдены"""

    status_code = status.HTTP_404_NOT_FOUND
    code = "order_details_not_found_error"
    message = "Order details not found"
