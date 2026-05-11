from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import (
    Float,
    Integer,
    String,
    Boolean,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
    Computed,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.models.mixins import TimestampMixin

from app.core.database import Base


if TYPE_CHECKING:
    from app.models import Category, User, Favorite, Review


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="positive_amount_check"),
        CheckConstraint("price >= 0.0", name="positive_price_check"),
        Index("ix_products_tsv_gin", "tsv", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, index=True)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    rating: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0"))

    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
        setweight(to_tsvector('english', coalesce(name, '')), 'A')
        || setweight(to_tsvector('russian', coalesce(name, '')), 'A')
        || setweight(to_tsvector('english', coalesce(description, '')), 'B')
        || setweight(to_tsvector('russian', coalesce(description, '')), 'B')
        """,
            persisted=True,
        ),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    seller: Mapped["User"] = relationship(back_populates="products")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="product")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"{self.name}, {self.price}"
