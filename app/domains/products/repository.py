from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    ProductNotFoundException,
)

from app.domains.products.schemas import ProductPartialUpdate, ProductPublic
from app.models import Category, Product


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
            .where(Product.is_active)
            .limit(limit)
            .offset(offset)
            .order_by(sort_by),
        )

        return [self._from_db(product) for product in products.all()]

    async def get_product(self, product_id: int):
        product = await self.session.scalar(
            select(Product).where(
                Product.id == product_id,
                Product.is_active,
            )
        )

        if product is None:
            raise ProductNotFoundException

        return self._from_db(product)

    async def get_products_by_category(self, category_id: int) -> list[ProductPublic]:
        if not await self._check_if_category_exists(category_id):
            raise CategoryNotFoundException

        products = await self.session.scalars(
            select(Product).where(
                Product.category_id == category_id,
                Product.is_active,
            )
        )

        return [self._from_db(product) for product in products.all()]

    async def create_product(self, create_product: ProductPublic):
        if not await self._check_if_category_exists(create_product.category_id):
            raise CategoryNotFoundException

        product = Product(**create_product.model_dump(), seller_id=8)
        self.session.add(product)
        await self.session.flush()

        return self._from_db(product)

    async def partial_update_product(
        self, product_id: int, patch_product: ProductPartialUpdate
    ):
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        for key, value in patch_product.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        return self._from_db(product)

    async def delete_product(self, product_id: int):
        product = await self._select_product_for_update(product_id)

        if not product:
            raise ProductNotFoundException

        product.is_active = False
        return {"message": "Product deleted"}
