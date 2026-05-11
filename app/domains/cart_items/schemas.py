from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    """
    Базовая модель, которая содержит минимальный набор полей, необходимых
    для идентификации товара и его количества в корзине.
    """

    product_id: int = Field(description="ID товара")
    quantity: int = Field(ge=1, description="Количество товара")


class CartItemCreate(CartItemBase):
    """Модель для добавления нового товара в корзину."""

    pass


class CartItemUpdate(BaseModel):
    """Модель для обновления количества товара в корзине."""

    quantity: int = Field(ge=1, description="Новое количество товара")


class ProductForCartItemSchema(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в Cart GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    price: float = Field(description="Цена товара в рублях", gt=0)
    image_url: str | None = Field(default=None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")

    model_config = ConfigDict(from_attributes=True)


class CartItemPublic(BaseModel):
    """Товар в корзине с данными продукта."""

    id: int = Field(..., description="ID позиции корзины")
    quantity: int = Field(ge=1, description="Количество товара")
    product: ProductForCartItemSchema = Field(description="Информация о товаре")

    model_config = ConfigDict(from_attributes=True)


class CartPublic(BaseModel):
    """Полная информация о корзине пользователя."""

    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItemPublic] = Field(description="Содержимое корзины")
    total_quantity: int = Field(ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)
