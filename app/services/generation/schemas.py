from dataclasses import dataclass


@dataclass
class ImagePayload:
    """
    Доменное представление одного изображения для генерации.

    Провайдер сам решает, что использовать: presigned_url или data.

    Attributes:
        position: Позиция фото ("front", "back", "left", "right").
        object_key: Ключ объекта в MinIO.
        content_type: MIME-тип изображения.
        filename: Исходное имя файла.
        presigned_url: Временная ссылка (для URL-режима).
        data: Байты файла (для direct-режима).
    """

    position: str
    object_key: str
    content_type: str
    filename: str
    presigned_url: str | None = None
    data: bytes | None = None