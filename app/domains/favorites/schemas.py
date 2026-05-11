from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FavoriteCreate(BaseModel):
    """
    Модель для создания избранного.
    Используется в POST запросах.
    """

    product_id: int = Field(description="ID товара")


class ProductForFavoriteSchema(BaseModel):
    """
    Модель для ответа с данными товара.
    Использвется для схемы FavoritePublic.
    """

    name: str = Field(description="Название товара")
    price: float = Field(description="Цена товара в рублях", gt=0)

    model_config = ConfigDict(from_attributes=True)


class FavoritePublic(BaseModel):
    """
    Модель для ответа с данными избранного товара.
    Используется в GET-запросах.
    """

    product: ProductForFavoriteSchema
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
