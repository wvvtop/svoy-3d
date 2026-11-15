from enum import Enum


class OrderStatus(str, Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    MODEL_READY = "MODEL_READY"
    FAILED = "FAILED"
    REVISION = "REVISION"


class PhotoStatus(str, Enum):
    UPLOADING = "UPLOADING"
    SCANNING = "SCANNING"
    UPLOADED = "UPLOADED"

class PhotoPosition(str, Enum):
    """Позиция фотографии автомобиля."""

    FRONT = "front"
    LEFT = "left"
    RIGHT = "right"
    BACK = "back"

class PhotoReviewStatus(str, Enum):
    PENDING  = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"