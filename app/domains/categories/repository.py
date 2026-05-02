from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.python_exceptions import CategoryNotFoundException
from app.models import Category
from app.domains.categories.schemas import (
    CategoryCreate,
    CategoryPartialUpdate,
    CategoryPublic,
)


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _from_db(model) -> CategoryPublic:
        return CategoryPublic.model_validate(model)

    async def _get_category_for_update(self, category_id: int) -> Category:
        return await self.session.scalar(
            select(Category)
            .where(
                Category.id == category_id,
                Category.is_active,
            )
            .with_for_update()
        )

    async def get_categories(
        self,
        offset: int,
        limit: int,
        sort_by: str,
        sort_order: str,
    ) -> list[CategoryPublic]:

        categories = await self.session.scalars(
            select(Category).offset(offset).limit(limit).order_by(sort_by)
        )
        return [self._from_db(category) for category in categories.all()]

    async def create_category(self, category: CategoryCreate) -> CategoryPublic:
        db_category = Category(**category.model_dump())
        self.session.add(db_category)
        await self.session.flush()

        return self._from_db(db_category)

    async def partial_update_category(
        self, category_id: int, category: CategoryPartialUpdate
    ) -> CategoryPublic:
        db_category = await self._get_category_for_update(category_id)
        if not db_category:
            raise CategoryNotFoundException

        for key, value in category.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)

        return self._from_db(db_category)

    async def delete_category(self, category_id: int) -> dict:
        db_category = await self._get_category_for_update(category_id)
        if not db_category:
            raise CategoryNotFoundException(category_id)

        db_category.is_active = False
        return {"message": "Category deleted"}
