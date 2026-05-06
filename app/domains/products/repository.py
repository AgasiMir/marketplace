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
    ProductPartialUpdate,
    ProductPublic,
)
from app.models import Category, Product
from app.models.user import User


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _from_db(model: Product) -> ProductPublic:
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

    async def get_all_products(self, offset: int, limit: int, sort_by: str):
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

        return [self._from_db(product) for product in products.all()]

    async def get_product(self, product_id: int):
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

        return self._from_db(product)

    async def get_products_by_category(self, category_id: int) -> list[ProductPublic]:
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

        return [self._from_db(product) for product in products.all()]

    async def create_product(
        self, create_product: ProductCreate, seller_id: int
    ) -> dict:
        if not await self._check_if_category_exists(create_product.category_id):
            raise CategoryNotFoundException

        product = Product(**create_product.model_dump(), seller_id=seller_id)
        self.session.add(product)
        await self.session.flush()

        return {"message": "Product created"}

    async def partial_update_product(
        self,
        product_id: int,
        patch_product: ProductPartialUpdate,
        seller_id: int,
    ) -> dict:
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        if product.seller_id != seller_id:
            raise CurrentProductSellerException

        for key, value in patch_product.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        return {"message": "Product updated"}

    async def delete_product(
        self, product_id: int, user_role: str, user_id: int
    ) -> dict:
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        if user_role == "seller" and product.seller_id != user_id:
            raise CurrentProductSellerException

        product.is_active = False
        return {"message": "Product deleted"}
