class GenerationError(Exception):
    """Базовая ошибка слоя генерации."""
    pass


class GenerationTemporaryError(GenerationError):
    """Временная — можно повторить."""
    pass


class GenerationPermanentError(GenerationError):
    """Постоянная — повторять бессмысленно."""
    pass


class GenerationProviderFailedError(GenerationError):
    """Провайдер сообщил, что генерация провалилась."""
    pass