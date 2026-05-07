from sqlalchemy import desc
from app.domains.products.schemas import (
    ProductCreate,
    ProductCreatePublic,
    ProductDeletePublic,
    ProductPartialUpdate,
    ProductPartialUpdatePublic,
    ProductPublic,
)
from app.email import send_email_async
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
        self,
        pagination: Pagination,
        sort_by: str,
        sort_order: str,
        user_id: int | None,
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
            offset=offset, limit=limit, sort_by=sort_by, user_id=user_id
        )

    async def get_product(self, product_id: int, user_id: int | None) -> ProductPublic:
        return await self.db_manager.products.get_product(product_id, user_id)

    async def get_products_by_category(
        self, category_id: int, user_id: int | None
    ) -> list[ProductPublic]:
        return await self.db_manager.products.get_products_by_category(
            category_id, user_id
        )

    async def create_product(
        self,
        create_product: ProductCreate,
        seller_id: int,
        email: str,
        username: str,
    ) -> ProductCreatePublic:
        res = await self.db_manager.products.create_product(create_product, seller_id)

        if res:
            send_email_async.delay(
                email,
                "Добавление Товара",
                body=f"""{username}. Вы дбавили товар:\n\nID: {res["product_id"]}
                \nНазвание: {res["product_name"]}\nЦена: {res["product_price"]}
                \nОписание товара: {res["product_description"]}""",
            )

            return res

    async def partial_update_product(
        self,
        product_id: int,
        patch_product: ProductPartialUpdate,
        seller_id: int,
        email: str,
        username: str,
    ) -> ProductPartialUpdatePublic:
        res = await self.db_manager.products.partial_update_product(
            product_id=product_id,
            patch_product=patch_product,
            seller_id=seller_id,
        )

        if res:
            send_email_async.delay(
                email,
                "Обновление Товара",
                body=f"""{username}. Вы обновили товар:\n\nID: {product_id}
                \nНазвание: {res["product_name"]}\nЦена: {res["product_price"]}
                \nОписание товара: {res["product_description"]}""",
            )
            return res

    async def delete_product(
        self,
        product_id: int,
        user_id: int,
        email: str,
        username: str,
        user_role: str,
    ) -> ProductDeletePublic:
        if user_role not in ("admin", "seller"):
            raise NotEnoughRightsException

        res = await self.db_manager.products.delete_product(
            product_id,
            user_role,
            user_id,
        )
        if res:
            if user_role == "seller":
                send_email_async.delay(
                    email,
                    "Удаление Товара",
                    body=f"""{username}. Вы удалили товар:\n\nID: {res["product_id"]}
                    \nНазвание: {res["product_name"]}\nЦена: {res["product_price"]}
                    \nОписание товара: {res["product_description"]}""",
                )

            if user_role == "admin":
                message = """Товар был удален, так как нарушал правила магазина. Просьба 
                связаться с администрацией для уточнения деталей."""
                send_email_async.delay(
                    res["seller_email"],
                    "Удаление Товара",
                    body=f"""{res["seller_username"]}. {message}
                    \n\nID: {res["product_id"]}
                    \nНазвание: {res["product_name"]}\nЦена: {res["product_price"]}
                    \nОписание товара: {res["product_description"]}""",
                )
            return res
