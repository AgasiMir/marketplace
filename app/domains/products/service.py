from sqlalchemy import desc
from app.domains.products.schemas import (
    ProductCreate,
    ProductPartialUpdate,
    ProductPublic,
)
from app.exceptions.python_exceptions import (
    NotEnoughRightsException,
    WrongSortByException,
)
from app.models import Product
from app.uow.uow import DBManager
from app.utils.utils import Pagination


class ProductService:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    async def get_all_products(
        self, pagination: Pagination, sort_by: str, sort_order: str
    ) -> list[ProductPublic]:

        LIST_OF_SORT_BY = ["id", "name", "price"]

        sort_by = sort_by

        if sort_by not in LIST_OF_SORT_BY:
            raise WrongSortByException

        sort_by = getattr(Product, sort_by)

        if sort_order == "desc":
            sort_by = desc(sort_by)

        page = pagination.page
        offset = (page - 1) * pagination.page_size.value
        limit = pagination.page_size.value

        return await self.db_manager.products.get_all_products(
            offset=offset,
            limit=limit,
            sort_by=sort_by,
        )

    async def get_product(self, product_id: int) -> ProductPublic:
        return await self.db_manager.products.get_product(product_id)

    async def get_products_by_category(self, category_id: int) -> list[ProductPublic]:
        return await self.db_manager.products.get_products_by_category(category_id)

    async def create_product(
        self, create_product: ProductCreate, seller_id: int
    ) -> dict:
        return await self.db_manager.products.create_product(create_product, seller_id)

    async def partial_update_product(
        self,
        product_id: int,
        patch_product: ProductPartialUpdate,
        seller_id: int,
    ) -> dict:
        return await self.db_manager.products.partial_update_product(
            product_id=product_id,
            patch_product=patch_product,
            seller_id=seller_id,
        )

    async def delete_product(self, product_id: int, current_user) -> dict:
        if current_user.role not in ("admin", "seller"):
            raise NotEnoughRightsException

        return await self.db_manager.products.delete_product(
            product_id,
            current_user.role,
            current_user.id,
        )
