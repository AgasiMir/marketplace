from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FavoriteCreate(BaseModel):
    product_id: int = Field(description="ID товара")


class ProductForFavoriteSchema(BaseModel):
    name: str = Field(description="Название товара")
    price: float = Field(description="Цена товара в рублях", gt=0)


class FavoritePublic(BaseModel):
    product: ProductForFavoriteSchema
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
