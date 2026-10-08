class GenAPIError(Exception):
    """Базовая ошибка GenAPI."""


class GenAPITemporaryError(GenAPIError):
    """Временная ошибка (network, timeout, 5xx) — можно повторить."""


class GenAPIPermanentError(GenAPIError):
    """Постоянная ошибка (4xx, невалидный запрос)."""


class GenAPIGenerationFailedError(GenAPIError):
    """Генерация завершилась статусом failed."""