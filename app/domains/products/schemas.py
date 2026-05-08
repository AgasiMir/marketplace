from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.domains.categories.schemas import CategoryForProductSchema
from app.domains.users.schemas import SellerForProductSchema


class ProductPublic(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: str | None = Field(default=None, description="Описание товара")
    price: float = Field(description="Цена товара в рублях", gt=0)
    image_url: str | None = Field(default=None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    is_active: bool = Field(description="Активность товара")

    created_at: datetime = Field(description="Время создания категории")
    updated_at: datetime = Field(description="Время последнего обновления категории")

    category: CategoryForProductSchema = Field(description="Категория товара")
    seller: SellerForProductSchema = Field(description="Имя продавца")

    is_favorite: bool = Field(default=False)
    rating: float = Field(description="Рейтинг товара")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """

    name: str = Field(
        min_length=3,
        max_length=100,
        description="Название товара (3-100 символов)",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Описание товара (до 500 символов)",
    )
    price: Decimal = Field(
        gt=0,
        description="Цена товара (больше 0)",
        decimal_places=2,
    )
    image_url: str | None = Field(
        None,
        max_length=200,
        description="URL изображения товара",
    )
    stock: int = Field(
        ge=0,
        description="Количество товара на складе (0 или больше)",
    )
    category_id: int = Field(description="ID категории, к которой относится товар")


class ProductPartialUpdate(BaseModel):
    """
    Модель для частичного обновления товара.
    Используется в PATCH запросах.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Название товара (3-100 символов)",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Описание товара (до 500 символов)",
    )
    price: Decimal | None = Field(
        default=None,
        gt=0,
        description="Цена товара (больше 0)",
        decimal_places=2,
    )
    image_url: str | None = Field(
        None,
        max_length=200,
        description="URL изображения товара",
    )
    stock: int | None = Field(
        default=None,
        ge=0,
        description="Количество товара на складе (0 или больше)",
    )
    category_id: int | None = Field(
        default=None,
        description="ID категории, к которой относится товар",
    )


class ProductURDPublic(BaseModel):
    message: str
    id: int
    name: str
    price: float
    description: str | None = None


class ProductAdminDeletePublic(ProductURDPublic):
    seller_email: EmailStr
    seller_username: str
