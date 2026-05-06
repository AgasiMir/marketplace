from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


if TYPE_CHECKING:
    from app.models import User, Product


class Favorite(TimestampMixin, Base):
    """Модель избранного пользователя

    Представляет связь между пользователем и товаром в списке избранного.

    Attributes:
        id: Уникальный идентификатор записи
        user_id: Идентификатор пользователя (внешний ключ)
        product_id: Идентификатор товара (внешний ключ)
        is_active: Флаг активности записи
        user: Связь с моделью User
        product: Связь с моделью Product
    """

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="unique_favorite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="favorites")
    product: Mapped["Product"] = relationship(back_populates="favorites")
