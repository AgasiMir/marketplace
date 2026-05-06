from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.exceptions.python_exceptions import (
    FavoriteAlreadyExistsException,
    FavoriteNotFoundException,
    FavoriteLimitExceededException,
    ProductNotFoundException,
)
from app.models import Favorite, Product, User, Category
from app.domains.favorites.schemas import FavoriteCreate, FavoritePublic


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_favorites(self, user_id: int) -> list[FavoritePublic]:
        favorites = await self.session.scalars(
            select(Favorite)
            .options(joinedload(Favorite.product))
            .where(Favorite.user_id == user_id)
        )

        return favorites.all()

    async def add_favorite(self, user_id: int, create_favorite: FavoriteCreate) -> dict:
        product_id = create_favorite.product_id

        # Проверяем лимит избранного
        favorites_count = await self.session.scalar(
            select(func.count(Favorite.id)).where(
                Favorite.user_id == user_id,
                Favorite.is_active,
            )
        )
        if favorites_count >= settings.FAVORITES_MAX_ITEMS:
            raise FavoriteLimitExceededException

        product = await self.session.scalar(
            select(Product)
            .join(Category, Product.category_id == Category.id)
            .join(User, Product.seller_id == User.id)
            .options(joinedload(Product.category))
            .options(joinedload(Product.seller))
            .where(
                Product.id == product_id,
                Product.is_active,
                User.is_active,
                Category.is_active,
            )
        )

        if product is None:
            raise ProductNotFoundException

        favorite = await self.session.scalar(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id,
            )
        )

        if favorite:
            raise FavoriteAlreadyExistsException

        favorite = Favorite(user_id=user_id, product_id=product_id)

        self.session.add(favorite)

        return {"message": "Favorite Added"}

    async def delete_favorite(self, user_id: int, product_id: int) -> dict:
        favorite = await self.session.scalar(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id,
            )
        )

        if not favorite:
            raise FavoriteNotFoundException

        await self.session.delete(favorite)

        return {"message": "Favorite deleted"}
