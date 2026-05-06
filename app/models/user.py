from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import StrEnum

from app.core.database import Base
from app.models.mixins import TimestampMixin


if TYPE_CHECKING:
    from app.models import Product, Favorite


class UserRole(StrEnum):
    buyer = "buyer"
    seller = "seller"
    admin = "admin"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=True),
        server_default="buyer",
        nullable=False,
    )

    products: Mapped[list["Product"]] = relationship(back_populates="seller")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return self.username
