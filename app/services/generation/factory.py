from app.services.generation.provider import GenerationProvider


class ProviderRegistry:
    """Реестр доступных провайдеров."""

    def __init__(self) -> None:
        self._providers: dict[str, GenerationProvider] = {}

    def register(self, provider: GenerationProvider) -> None:
        """
        Регистрирует провайдера.

        Args:
            provider: Экземпляр GenerationProvider.
        """

        self._providers[provider.name] = provider

    def get(self, name: str) -> GenerationProvider:
        """
        Возвращает провайдера по имени.

        Args:
            name: Имя провайдера.

        Returns:
            GenerationProvider: Найденный провайдер.

        Raises:
            ValueError: Если провайдер не зарегистрирован.
        """

        if name not in self._providers:
            raise ValueError(
                f"Provider '{name}' не зарегистрирован. "
                f"Доступные: {list(self._providers)}"
            )
        return self._providers[name]

    def has(self, name: str) -> bool:
        """
        Проверяет, зарегистрирован ли провайдер.

        Args:
            name: Имя провайдера.

        Returns:
            bool: True, если провайдер есть в реестре.
        """

        return name in self._providers


provider_registry = ProviderRegistry()