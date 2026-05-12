from datetime import datetime
from decimal import Decimal


from pydantic import BaseModel, Field, ConfigDict

from app.domains.cart_items.schemas import ProductForCartItemSchema


class OrderItemPublic(BaseModel):
    """
    Используется в ответах API при возврате деталей заказа.
    """

    id: int = Field(description="ID позиции заказа")
    product_id: int = Field(description="ID товара")
    quantity: int = Field(ge=1, description="Количество")
    unit_price: Decimal = Field(ge=0, description="Цена за единицу на момент покупки")
    total_price: Decimal = Field(ge=0, description="Сумма по позиции")
    product: ProductForCartItemSchema | None = Field(
        default=None,
        description="Полная информация о товаре",
    )

    model_config = ConfigDict(from_attributes=True)


class OrderPublic(BaseModel):
    """
    Используется в ответах API при создании заказа, просмотре одного заказа и в списках.
    Включает статус, общую сумму, временные метки и список items
    """

    id: int = Field(description="ID заказа")
    user_id: int = Field(description="ID пользователя")
    status: str = Field(description="Текущий статус заказа")
    total_amount: Decimal = Field(ge=0, description="Общая стоимость")
    created_at: datetime = Field(description="Когда заказ был создан")
    updated_at: datetime = Field(description="Когда последний раз обновлялся")
    items: list[OrderItemPublic] = Field(description="Список позиций")

    model_config = ConfigDict(from_attributes=True)


class OrderListPublic(BaseModel):
    """
    Обёртка для пагинированных списков заказов. Возвращается в GET /orders и
    содержит массив заказов, общее количество, текущую страницу и размер страницы.
    """

    items: list[OrderPublic] = Field(description="Заказы на текущей странице")
    total: int = Field(ge=0, description="Общее количество заказов")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")

    model_config = ConfigDict(from_attributes=True)
