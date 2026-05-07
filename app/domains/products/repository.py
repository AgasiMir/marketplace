from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    CurrentProductSellerException,
    ProductNotFoundException,
)

from app.domains.products.schemas import (
    ProductCreate,
    ProductCreatePublic,
    ProductDeletePublic,
    ProductPartialUpdate,
    ProductPartialUpdatePublic,
    ProductPublic,
)
from app.models import Category, Product, Favorite
from app.models.user import User


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _from_db(self, model: Product, user_id: int | None) -> ProductPublic:
        if user_id:
            current_usres_favorites = await self.session.scalars(
                select(Favorite).where(Favorite.user_id == user_id)
            )
            if current_usres_favorites:
                for favorite in current_usres_favorites:
                    if favorite.product_id == model.id:
                        favorite_product = ProductPublic.model_validate(model)
                        favorite_product.is_favorite = True
                        return favorite_product
        return ProductPublic.model_validate(model)

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

        return [await self._from_db(product, user_id) for product in products.all()]

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

        return await self._from_db(product, user_id)

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

        return [await self._from_db(product, user_id) for product in products.all()]

    async def create_product(
        self, create_product: ProductCreate, seller_id: int
    ) -> ProductCreatePublic:
        if not await self._check_if_category_exists(create_product.category_id):
            raise CategoryNotFoundException

        product = Product(**create_product.model_dump(), seller_id=seller_id)
        self.session.add(product)
        await self.session.flush()

        return {
            "message": "Product created",
            "product_name": product.name,
            "product_id": product.id,
            "product_price": product.price,
            "product_description": product.description,
        }

    async def partial_update_product(
        self,
        product_id: int,
        patch_product: ProductPartialUpdate,
        seller_id: int,
    ) -> ProductPartialUpdatePublic:
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        if product.seller_id != seller_id:
            raise CurrentProductSellerException

        for key, value in patch_product.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        return {
            "message": "Product updated",
            "product_name": product.name,
            "product_id": product.id,
            "product_price": product.price,
            "product_description": product.description,
        }

    async def delete_product(
        self, product_id: int, user_role: str, user_id: int
    ) -> ProductDeletePublic:
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        if user_role == "seller" and product.seller_id != user_id:
            raise CurrentProductSellerException

        if user_role == "seller":
            product.is_active = False

            return {
                "message": "Product deleted",
                "product_name": product.name,
                "product_id": product.id,
                "product_price": product.price,
                "product_description": product.description,
            }

        if user_role == "admin":
            product = await self.session.scalar(
                select(Product)
                .options(joinedload(Product.seller))
                .where(Product.id == product_id, Product.is_active)
            )

            product.is_active = False

            return {
                "message": "Product deleted",
                "product_name": product.name,
                "product_id": product.id,
                "product_price": product.price,
                "product_description": product.description,
                "seller_email": product.seller.email,
                "seller_username": product.seller.username,
            }
