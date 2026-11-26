"""Общие типы для курсорной пагинации."""

from datetime import datetime
from typing import Literal


# Разрешённые поля сортировки заказов.
OrderSortField = Literal["created_at", "id"]

# Направление сортировки.
SortDirection = Literal["asc", "desc"]

# Допустимые типы значений курсора заказов.
CursorValue = datetime | int