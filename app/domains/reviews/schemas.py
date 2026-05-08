from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewPublic(BaseModel):
    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="ID пользователя, оставившего отзыв")
    product_id: int = Field(description="ID товара, к которому относится отзыв")
    comment: str | None = Field(description="Комментарий к отзыву")
    created_at: datetime = Field(description="Время создания отзыва")
    grade: int = Field(description="Оценка от 1 до 5")
    is_active: bool = Field(description="Активен ли отзыв")

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    product_id: int = Field(description="ID товара")
    comment: str | None = Field(default=None, description="Комментарий к отзыву")
    grade: int | None = Field(default=None, description="Оценка от 1 до 5", ge=1, le=5)
