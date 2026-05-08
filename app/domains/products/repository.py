from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.reviews.schemas import ReviewPublic
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    CurrentProductSellerException,
    ProductNotFoundException,
)

from app.domains.products.schemas import (
    ProductAdminDeletePublic,
    ProductCreate,
    ProductPartialUpdate,
    ProductPublic,
    ProductURDPublic,
)
from app.models import Category, Product, Favorite, Review
from app.models.user import User


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _from_db(
        self,
        model: Product,
        user_id: int | None,
        favorite_product_ids: set[int] | None = None,
    ) -> ProductPublic:
        product = ProductPublic.model_validate(model)
        if user_id:
            # Если переданы предзагруженные ID избранных продуктов, используем их
            if favorite_product_ids is not None:
                if model.id in favorite_product_ids:
                    product.is_favorite = True

        return product

    async def _check_if_category_exists(self, category_id: int) -> bool:
        category = await self.session.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.is_active,
            )
        )

        return True if category else False

    async def _select_product_for_update(self, product_id: int):
        return await self.session.scalar(
            select(Product)
            .where(
                Product.id == product_id,
                Product.is_active,
            )
            .with_for_update()
        )

    async def get_all_products(
        self,
        offset: int,
        limit: int,
        sort_by: str,
        user_id: int | None,
    ):
        products = await self.session.scalars(
            select(Product)
            .join(Category, Product.category_id == Category.id)
            .join(User, Product.seller_id == User.id)
            .options(joinedload(Product.category))
            .options(joinedload(Product.seller))
            .where(
                Product.is_active,
                User.is_active,
                Category.is_active,
            )
            .order_by(sort_by)
            .limit(limit)
            .offset(offset)
        )

        favorite_product_ids = set()
        if user_id:
            favorite_ids = await self.session.scalars(
                select(Favorite.product_id).where(Favorite.user_id == user_id)
            )
            favorite_product_ids = set(favorite_ids.all())

        return [
            await self._from_db(product, user_id, favorite_product_ids)
            for product in products.all()
        ]

    async def get_product(self, product_id: int, user_id: int | None):
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

        favorite_product_ids = set()
        if user_id:
            favorite_ids = await self.session.scalars(
                select(Favorite.product_id).where(Favorite.user_id == user_id)
            )
            favorite_product_ids = set(favorite_ids.all())

        return await self._from_db(product, user_id, favorite_product_ids)

    async def get_products_by_category(
        self,
        category_id: int,
        user_id: int | None,
    ) -> list[ProductPublic]:
        if not await self._check_if_category_exists(category_id):
            raise CategoryNotFoundException

        products = await self.session.scalars(
            select(Product)
            .join(Category, Product.category_id == Category.id)
            .join(User, Product.seller_id == User.id)
            .options(joinedload(Product.category))
            .options(joinedload(Product.seller))
            .where(
                Product.category_id == category_id,
                Product.is_active,
                User.is_active,
                Category.is_active,
            )
        )

        favorite_product_ids = set()
        if user_id:
            favorite_ids = await self.session.scalars(
                select(Favorite.product_id).where(Favorite.user_id == user_id)
            )
            favorite_product_ids = set(favorite_ids.all())

        return [
            await self._from_db(product, user_id, favorite_product_ids)
            for product in products.all()
        ]

    async def create_product(
        self, create_product: ProductCreate, seller_id: int
    ) -> ProductURDPublic:
        if not await self._check_if_category_exists(create_product.category_id):
            raise CategoryNotFoundException

        product = Product(**create_product.model_dump(), seller_id=seller_id)
        self.session.add(product)
        await self.session.flush()

        data = {
            "message": "Product created",
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
        }

        return ProductURDPublic(**data)

    async def partial_update_product(
        self,
        product_id: int,
        patch_product: ProductPartialUpdate,
        seller_id: int,
    ) -> ProductURDPublic:
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        if product.seller_id != seller_id:
            raise CurrentProductSellerException

        for key, value in patch_product.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        data = {
            "message": "Product updated",
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
        }

        return ProductURDPublic(**data)

    async def delete_product(
        self, product_id: int, user_role: str, user_id: int
    ) -> ProductURDPublic | ProductAdminDeletePublic:
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        if user_role == "seller" and product.seller_id != user_id:
            raise CurrentProductSellerException

        if user_role == "seller":
            product.is_active = False

            data = {
                "message": "Product deleted",
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
            }

            return ProductURDPublic(**data)

        if user_role == "admin":
            product = await self.session.scalar(
                select(Product)
                .options(joinedload(Product.seller))
                .where(Product.id == product_id, Product.is_active)
            )

            product.is_active = False

            data = {
                "message": "Product deleted",
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "seller_email": product.seller.email,
                "seller_username": product.seller.username,
            }

            return ProductAdminDeletePublic(**data)

    async def get_product_reviews(self, product_id: int) -> list[ReviewPublic]:
        product = await self.session.scalar(
            select(Product)
            .join(Product.category)
            .join(Product.seller)
            .where(
                Product.id == product_id,
                Product.is_active,
                Category.is_active,
                User.is_active,
            )
        )
        if not product:
            raise ProductNotFoundException

        reviews = await self.session.scalars(
            select(Review)
            .options(joinedload(Review.user))
            .where(
                Review.product_id == product_id,
                Review.is_active,
            )
        )

        return [ReviewPublic.model_validate(review) for review in reviews.all()]
