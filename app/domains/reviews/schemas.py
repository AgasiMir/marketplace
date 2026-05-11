from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.domains.users.schemas import UserForReviewSchema


class ReviewPublic(BaseModel):
    """
    Схема для публичного представления отзыва.

    Используется для отображения отзыва в API, содержит все необходимые поля
    для отображения информации об отзыве, включая данные пользователя.

    Attributes:
        id: Уникальный идентификатор отзыва.
        user_id: ID пользователя, оставившего отзыв.
        product_id: ID товара, к которому относится отзыв.
        comment: Комментарий к отзыву (может быть None).
        created_at: Время создания отзыва.
        grade: Оценка от 1 до 5.
        is_active: Активен ли отзыв.
        user: Данные пользователя, ставившего отзыв в формате UserForReviewSchema.
    """

    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="ID пользователя, оставившего отзыв")
    product_id: int = Field(description="ID товара, к которому относится отзыв")
    comment: str | None = Field(description="Комментарий к отзыву")
    created_at: datetime = Field(description="Время создания отзыва")
    grade: int = Field(description="Оценка от 1 до 5")
    is_active: bool = Field(description="Активен ли отзыв")

    user: UserForReviewSchema

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """
    Схема для создания нового отзыва.

    Используется при получении данных от клиента для создания отзыва.
    Все поля, кроме product_id, являются необязательными.

    Attributes:
        product_id: ID товара, к которому оставляется отзыв (обязательное поле).
        comment: Комментарий к отзыву (опционально).
        grade: Оценка от 1 до 5 (опционально, с валидацией диапазона).
    """

    product_id: int = Field(description="ID товара")
    comment: str | None = Field(default=None, description="Комментарий к отзыву")
    grade: int | None = Field(default=None, description="Оценка от 1 до 5", ge=1, le=5)
