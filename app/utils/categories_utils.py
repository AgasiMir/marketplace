from enum import IntEnum, StrEnum
from pydantic import BaseModel, Field


class PageSize(IntEnum):
    SMALL = 10
    MEDIUM = 20
    LARGE = 50


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class SortBy(StrEnum):
    # Используем 'id' для сортировки вместо 'created_at' для лучшей производительности
    # Работает потому, что id автоматически увеличивается и соответствует времени создания

    ID = "created_at"
    NAME = "name"


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, description="Номер страницы")
    page_size: PageSize = Field(description="Размер страницы")
