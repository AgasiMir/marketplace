from typing import Annotated
from fastapi import Depends
from app.core.database import async_session
from app.domains.categories.service import CategoryService
from app.uow.uow import DBManager
from app.utils.categories_utils import Pagination


async def get_db():
    async with DBManager(session_factory=async_session) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_category_service(db_manager: DBDep) -> CategoryService:
    return CategoryService(db_manager=db_manager)


PaginationDep = Annotated[Pagination, Depends()]

CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
