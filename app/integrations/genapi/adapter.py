from app.integrations.genapi.client import GenAPIClient
from app.integrations.genapi.exceptions import (
    GenAPIPermanentError,
    GenAPITemporaryError,
)
from app.integrations.genapi.schemas import GenAPIStatusResponse
from app.schemas.enums.order import PhotoPosition
from app.services.generation.exceptions import (
    GenerationPermanentError,
    GenerationTemporaryError,
)
from app.services.generation.provider import (
    GenerationHandle,
    GenerationProvider,
    GenerationStatusResult,
    ProviderStatus,
)
from app.services.generation.schemas import ImagePayload


# GenAPI-специфичные имена параметров изображений
_IMAGE_PARAM_NAMES: dict[PhotoPosition, str] = {
    PhotoPosition.FRONT: "front_image",
    PhotoPosition.BACK: "back_image",
    PhotoPosition.LEFT: "left_image",
    PhotoPosition.RIGHT: "right_image",
}


# GenAPI-статус → доменный статус
_STATUS_MAP: dict[str, ProviderStatus] = {
    "starting": ProviderStatus.QUEUED,
    "queued": ProviderStatus.QUEUED,
    "pending": ProviderStatus.QUEUED,
    "processing": ProviderStatus.PROCESSING,
    "running": ProviderStatus.PROCESSING,
    "success": ProviderStatus.SUCCEEDED,
    "succeeded": ProviderStatus.SUCCEEDED,
    "failed": ProviderStatus.FAILED,
    "error": ProviderStatus.FAILED,
}


class GenAPIProvider(GenerationProvider):
    """Адаптер GenAPI к доменному интерфейсу GenerationProvider."""

    name = "genapi"

    def __init__(
        self,
        client: GenAPIClient,
        image_source: str = "minio",
    ) -> None:
        """
        Args:
            client: Низкоуровневый GenAPIClient.
            image_source: "minio" (presigned URL) или "direct" (bytes).
        """

        self._client = client
        self._image_source = image_source
        self.supports_presigned_urls = image_source == "minio"

    async def start_generation(
        self,
        images: dict[PhotoPosition, ImagePayload],
        *,
        mode: str = "multi_view",
    ) -> GenerationHandle: 
        
        params = self._build_image_params(images)

        try:
            resp = await self._client.create_generation(
                image_params=params,
                mode=mode,
            )
        except GenAPITemporaryError as exc:
            raise GenerationTemporaryError(str(exc)) from exc
        except GenAPIPermanentError as exc:
            raise GenerationPermanentError(str(exc)) from exc

        return GenerationHandle(
            provider_name=self.name,
            external_id=resp.request_id,
        )

    async def get_status(
        self,
        handle: GenerationHandle,
    ) -> GenerationStatusResult:
        """
        Опрашивает статус у GenAPI и маппит в доменный.

        Args:
            handle: Handle с external_id.

        Returns:
            GenerationStatusResult: Доменный статус.
        """

        try:
            resp = await self._client.get_status(handle.external_id)
        except GenAPITemporaryError as exc:
            raise GenerationTemporaryError(str(exc)) from exc
        except GenAPIPermanentError as exc:
            raise GenerationPermanentError(str(exc)) from exc

        domain_status = _STATUS_MAP.get(
            resp.status.lower(),
            ProviderStatus.PROCESSING,
        )

        return GenerationStatusResult(
            status=domain_status,
            raw=resp.raw,
        )

    async def download_result(
        self,
        handle: GenerationHandle,
    ) -> bytes:
        """
        Извлекает URL модели и скачивает .glb.

        Args:
            handle: Handle с external_id.

        Returns:
            bytes: Содержимое .glb.

        Raises:
            GenerationTemporaryError: Если генерация ещё не готова.
            GenerationPermanentError: Если URL не найден в ответе.
        """

        resp = await self._client.get_status(handle.external_id)

        if resp.status.lower() != "success":
            raise GenerationTemporaryError(
                f"GenAPI ещё не готов: {resp.status}"
            )

        model_url = self._extract_model_url(resp)

        if not model_url:
            raise GenerationPermanentError(
                f"URL модели не найден в ответе GenAPI: {resp.raw}"
            )

        return await self._client.download_model(model_url)

    # ── helpers ──

    def _build_image_params(
        self,
        images: dict[PhotoPosition, ImagePayload],
    ) -> dict:
        """
        Превращает доменные ImagePayload в формат GenAPI.

        Args:
            images: Доменные изображения.

        Returns:
            dict: Параметры вида {"front_image_url": "..."} или
                  {"front_image_url": (filename, bytes, ctype)}.

        Raises:
            GenerationPermanentError: Если payload не заполнен корректно.
        """

        params: dict = {}

        for position, payload in images.items():
            name = _IMAGE_PARAM_NAMES.get(position)
            if name is None:
                raise GenerationPermanentError(
                    f"Нет маппинга для позиции {position}"
                )

            if self._image_source == "minio":
                if not payload.presigned_url:
                    raise GenerationPermanentError(
                        f"presigned_url не задан для {position.value}"
                    )
                params[f"{name}_url"] = payload.presigned_url
            else:
                if payload.data is None:
                    raise GenerationPermanentError(
                        f"data не задан для {position.value}"
                    )
                params[f"{name}_url"] = (
                    payload.filename,
                    payload.data,
                    payload.content_type,
                )

        return params

    @staticmethod
    def _extract_model_url(resp: GenAPIStatusResponse) -> str | None:
        """
        Извлекает URL модели из ответа GenAPI.

        Поддерживает:
        - result: ["https://...glb"]
        - full_response: [{"url": "https://...glb"}]
        - output: {"model_url": "..."}  (на будущее)

        Args:
            resp: Ответ клиента.
        Returns:
            str | None: URL или None, если не найд

        """
    
        # result — список строк
        if resp.result:
            for item in resp.result:
                if isinstance(item, str) and item.startswith("http"):
                    return item
                if isinstance(item, dict):
                    url = item.get("url")
                    if isinstance(url, str) and url.startswith("http"):
                        return url
    
        # full_response — список dict-ов
        if resp.full_response:
            for item in resp.full_response:
                if isinstance(item, dict):
                    url = item.get("url") or item.get("model_url")
                    if isinstance(url, str) and url.startswith("http"):
                        return url
    
        # output — на случай других сетей
        if resp.output:
            for key in ("model_url", "glb_url", "url"):
                value = resp.output.get(key)
                if isinstance(value, str) and value.startswith("http"):
                    return value
    
        return None

