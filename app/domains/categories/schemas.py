from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryPublic(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")
    parent_id: int | None = Field(
        default=None,
        description="ID родительской категории, если есть",
    )
    is_active: bool = Field(description="Активна ли категория")
    created_at: datetime = Field(description="Время создания категории")
    updated_at: datetime = Field(description="Время последнего обновления категории")

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """

    name: str = Field(
        min_length=3,
        max_length=50,
        description="Название категории (3-50 символов)",
    )
    parent_id: int | None = Field(
        description="ID родительской категории, если есть",
        default=None,
    )


class CategoryPartialUpdate(BaseModel):
    """
    Модель для обновления категории.
    Используется в PATCH запросах.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Название категории (3-50 символов)",
    )
    parent_id: int | None = Field(
        default=None,
        description="ID родительской категории, если есть",
    )


class CategoryForProductSchema(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в Product GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")

    model_config = ConfigDict(from_attributes=True)
