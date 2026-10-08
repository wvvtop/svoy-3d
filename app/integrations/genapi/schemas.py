from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenAPICreateResponse:
    """
    Ответ GenAPI на создание генерации.

    Attributes:
        request_id: ID задачи у GenAPI.
        status: Начальный статус.
        raw: Сырой ответ для отладки.
    """

    request_id: str
    status: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenAPIStatusResponse:
    """
    Ответ GenAPI на запрос статуса.

    Attributes:
        request_id: ID задачи.
        status: Статус ("success", "processing", "failed", ...).
        result: Список URL-ов готовых файлов.
        full_response: Список dict-ов с url.
        output: Альтернативное поле для других сетей.
        raw: Сырой ответ целиком.
    """

    request_id: str
    status: str
    result: list[str] | None = None
    full_response: list[dict[str, Any]] | None = None
    output: dict[str, Any] | None = None       # оставляем для совместимости
    raw: dict[str, Any] | None = None