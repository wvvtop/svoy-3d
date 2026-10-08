from app.servers.admin.config import AdminConfig
from app.integrations.genapi.adapter import GenAPIProvider
from app.integrations.genapi.client import GenAPIClient
from app.services.generation.factory import provider_registry


def build_providers(config: AdminConfig) -> None:
    """
    Регистрирует доступных провайдеров в provider_registry.

    Создаёт GenAPIClient и GenAPIProvider на основе конфига.

    Args:
        config: AdminConfig с настройками генерации и GenAPI.
    """

    genapi_client = GenAPIClient(
        api_key=config.GENAPI_API_KEY,
        base_url=config.GENAPI_BASE_URL,
        network=config.GENAPI_NETWORK,
        model=config.GENAPI_MODEL,
        request_timeout=config.GENERATION_REQUEST_TIMEOUT,
        download_timeout=config.GENERATION_DOWNLOAD_TIMEOUT,
    )

    provider_registry.register(
        GenAPIProvider(
            client=genapi_client,
            image_source=config.GENAPI_IMAGE_SOURCE,
        )
    )

    # ── Будущие провайдеры ──────────────────────────────
    # provider_registry.register(
    #     ReplicateProvider(api_token=config.REPLICATE_API_TOKEN)
    # )