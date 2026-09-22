from enum import Enum


class OrderStatus(str, Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    MODEL_READY = "MODEL_READY"
    FAILED = "FAILED"


class PhotoStatus(str, Enum):
    UPLOADING = "UPLOADING"
    SCANNING = "SCANNING"
    UPLOADED = "UPLOADED"
    REJECTED = "REJECTED"

class PhotoPosition(str, Enum):
    """Позиция фотографии автомобиля."""

    FRONT = "front"
    LEFT = "left"
    RIGHT = "right"
    BACK = "back"