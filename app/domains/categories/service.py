from sqlalchemy import desc
from app.uow.uow import DBManager
from app.domains.categories.schemas import (
    CategoryCreate,
    CategoryPartialUpdate,
    CategoryPublic,
)
from app.utils.categories_utils import Pagination


class CategoryService:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    async def get_categories(
        self, pagination: Pagination, sort_by: str, sort_order: str
    ) -> list[CategoryPublic]:

        LIST_OF_SORT_BY = ["id", "name"]

        sort_by = sort_by.lower()

        if sort_by not in LIST_OF_SORT_BY:
            raise ValueError("Invalid sort_by value")

        if sort_order == "desc":
            sort_by = desc(sort_by)

        page = pagination.page
        offset = (page - 1) * pagination.page_size.value
        limit = pagination.page_size.value

        return await self.db_manager.categories.get_categories(
            offset=offset,
            limit=limit,
            sort_by=sort_by,
        )

    async def create_category(self, category: CategoryCreate) -> CategoryPublic:
        return await self.db_manager.categories.create_category(category)

    async def partial_update_category(
        self, category_id: int, category: CategoryPartialUpdate
    ) -> CategoryPublic:
        return await self.db_manager.categories.partial_update_category(
            category_id, category
        )

    async def delete_category(self, category_id: int) -> dict:
        return await self.db_manager.categories.delete_category(category_id)
