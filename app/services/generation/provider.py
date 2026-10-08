from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.schemas.enums.order import PhotoPosition


class ProviderStatus(str, Enum):
    """Доменные статусы генерации (общие для всех провайдеров)."""

    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass
class GenerationHandle:
    """
    Идентификатор задачи во внешнем сервисе.

    Attributes:
        provider_name: Имя провайдера (например, "genapi").
        external_id: ID задачи у провайдера.
    """

    provider_name: str
    external_id: str


@dataclass
class GenerationStatusResult:
    """
    Результат опроса статуса генерации.

    Attributes:
        status: Доменный статус (ProviderStatus).
        progress: Прогресс в процентах (0–100) или None.
        error: Текст ошибки, если генерация провалилась.
        raw: Сырой ответ провайдера для отладки.
    """
    status: ProviderStatus
    progress: int | None = None
    error: str | None = None
    raw: dict[str, Any] | None = None


class GenerationProvider(ABC):
    """
    Интерфейс провайдера генерации 3D-моделей.

    Реализации: GenAPIProvider, ReplicateProvider, MeshyProvider, SelfHostedProvider…
    """

    name: str
    supports_presigned_urls: bool = False

    @abstractmethod
    async def start_generation(
        self,
        images: dict[PhotoPosition, "ImagePayload"],
        *,
        mode: str = "multi_view",
    ) -> GenerationHandle:
        """
        Запускает генерацию у провайдера.

        Args:
            images: Словарь {PhotoPosition: ImagePayload}.
            mode: Режим генерации ("multi_view" | "single_view").

        Returns:
            GenerationHandle: Идентификатор запущенной задачи.

        Raises:
            GenerationTemporaryError: При временной ошибке (можно повторить).
            GenerationPermanentError: При постоянной ошибке.
        """

    @abstractmethod
    async def get_status(
        self,
        handle: GenerationHandle,
    ) -> GenerationStatusResult:
        """
        Возвращает доменный статус задачи.

        Args:
            handle: Идентификатор задачи.

        Returns:
            GenerationStatusResult: Текущий статус и метаданные.
        """

    @abstractmethod
    async def download_result(
        self,
        handle: GenerationHandle,
    ) -> bytes:
        """
        Скачивает готовый .glb-файл.

        Args:
            handle: Идентификатор задачи.

        Returns:
            bytes: Содержимое .glb.

        Raises:
            GenerationTemporaryError: Временная ошибка скачивания.
            GenerationProviderFailedError: Провайдер сообщил о провале.
        """


# Отложенный импорт для избежания цикла
from app.services.generation.schemas import ImagePayload  # noqa: E402