from typing import Any

import httpx

from app.integrations.genapi.exceptions import (
    GenAPIPermanentError,
    GenAPITemporaryError,
)
from app.integrations.genapi.schemas import (
    GenAPICreateResponse,
    GenAPIStatusResponse,
)


class GenAPIClient:
    """
    HTTP-клиент GenAPI на httpx.

    Держит два клиента:
    - api_client — для запросов к GenAPI;
    - download_client — для скачивания тяжёлых файлов.

    Жизненный цикл: создаётся один раз в Worker-е,
    закрывается при остановке.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        network: str,
        model: str,
        request_timeout: int = 60,
        download_timeout: int = 300,
    ) -> None:
        """
        Создаёт клиент и оба httpx.AsyncClient.

        Args:
            api_key: Bearer-токен GenAPI.
            base_url: Базовый URL (например, https://api.gen-api.ru).
            network: Имя сети GenAPI.
            model: Имя модели.
            request_timeout: Таймаут API-запросов (сек).
            download_timeout: Таймаут скачивания файлов (сек).
        """
        
        self._base_url = base_url.rstrip("/")
        self._network = network
        self._model = model

        self._api_client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(
                request_timeout,
                connect=10.0,
            ),
        )

        self._download_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                download_timeout,
                connect=10.0,
                read=download_timeout,
            ),
        )

    async def close(self) -> None:
        """Закрывает оба HTTP-клиента."""

        await self._api_client.aclose()
        await self._download_client.aclose()

    # ── helpers ──────────────────────────────────────────

    def _create_url(self) -> str:
        """
        Возвращает URL эндпоинта создания генерации.

        Returns:
            str: Полный URL.
        """
        
        return f"/api/v1/networks/{self._network}"

    def _status_url(self, request_id: str) -> str:
        """
        Возвращает URL эндпоинта статуса.

        Args:
            request_id: ID задачи GenAPI.

        Returns:
            str: Полный URL.
        """

        return f"/api/v1/request/get/{request_id}"

    @staticmethod
    def _raise_for_status(status_code: int, body: str) -> None:
        """
        Проверяет HTTP-статус и кидает соответствующее исключение.

        Args:
            status_code: HTTP-код ответа.
            body: Тело ответа (для сообщения).

        Raises:
            GenAPITemporaryError: При 5xx.
            GenAPIPermanentError: При 4xx.
        """

        if status_code >= 500:
            raise GenAPITemporaryError(
                f"GenAPI server error {status_code}: {body[:500]}"
            )
        if status_code >= 400:
            raise GenAPIPermanentError(
                f"GenAPI client error {status_code}: {body[:500]}"
            )

    # ── публичные методы ─────────────────────────────────

    async def create_generation(
        self,
        image_params: dict[str, Any],
        *,
        mode: str = "multi_view",
    ) -> GenAPICreateResponse:
        """
        Запускает генерацию у GenAPI (JSON или multipart).

        Args:
            image_params: Параметры изображений от адаптера.
            mode: Режим генерации.

        Returns:
            GenAPICreateResponse: Ответ с request_id.

        Raises:
            GenAPITemporaryError: Временная ошибка сети.
            GenAPIPermanentError: Постоянная ошибка (4xx).
        """

        uses_files = any(
            isinstance(v, tuple) for v in image_params.values()
        )

        try:
            if uses_files:
                data: dict[str, Any] = {
                    "model": self._model,
                    "mode": mode,
                }
                files: dict[str, tuple] = {}

                for key, value in image_params.items():
                    if isinstance(value, tuple):
                        filename, content, ctype = value
                        files[key] = (filename, content, ctype)
                    else:
                        data[key] = value

                resp = await self._api_client.post(
                    self._create_url(),
                    data=data,
                    files=files or None,
                )
            else:
                payload = {
                    "model": self._model,
                    "mode": mode,
                    **image_params,
                }
                resp = await self._api_client.post(
                    self._create_url(),
                    json=payload,
                )

            self._raise_for_status(resp.status_code, resp.text)
            data = resp.json()

        except httpx.TimeoutException as exc:
            raise GenAPITemporaryError(
                f"GenAPI timeout: {exc}"
            ) from exc
        except httpx.TransportError as exc:
            raise GenAPITemporaryError(
                f"GenAPI transport error: {exc}"
            ) from exc

        return GenAPICreateResponse(
            request_id=str(data["request_id"]),
            status=str(data.get("status", "starting")),
            raw=data,
        )

    async def get_status(self, request_id: str) -> GenAPIStatusResponse:
        """
        Возвращает статус задачи GenAPI.

        Args:
            request_id: ID задачи.

        Returns:
            GenAPIStatusResponse: Статус, result, full_response.
        """

        try:
            resp = await self._api_client.get(
                self._status_url(request_id),
            )
            self._raise_for_status(resp.status_code, resp.text)
            data = resp.json()
    
        except httpx.TimeoutException as exc:
            raise GenAPITemporaryError(
                f"GenAPI status timeout: {exc}"
            ) from exc
        except httpx.TransportError as exc:
            raise GenAPITemporaryError(
                f"GenAPI status transport error: {exc}"
            ) from exc
    
        return GenAPIStatusResponse(
            request_id=request_id,
            status=str(data.get("status", "unknown")),
            result=data.get("result"),
            full_response=data.get("full_response"),
            output=data.get("output"),
            raw=data,
        )

    async def download_model(self, url: str) -> bytes:
        """
        Скачивает .glb по прямой ссылке.

        Args:
            url: URL модели.

        Returns:
            bytes: Содержимое файла.
        """

        try:
            resp = await self._download_client.get(url)
            self._raise_for_status(resp.status_code, "")
            return resp.content

        except httpx.TimeoutException as exc:
            raise GenAPITemporaryError(
                f"GenAPI download timeout: {exc}"
            ) from exc
        except httpx.TransportError as exc:
            raise GenAPITemporaryError(
                f"GenAPI download transport error: {exc}"
            ) from exc