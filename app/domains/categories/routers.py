from fastapi import APIRouter, Depends, status

from app.domains.categories.schemas import (
    CategoryCreate,
    CategoryPartialUpdate,
    CategoryPublic,
)
from app.domains.dependencies import CategoryServiceDep, PaginationDep
from app.utils.categories_utils import SortBy, SortOrder


from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter


from app.exceptions.python_exceptions import CategoryNotFoundException
from app.exceptions.fastapi_exceptions import CategoryNotFoundHTTPException

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.SECOND * 2))))],
)


@router.get(
    "",
    summary="Get categories",
    description="Эндпойнт для получения категорий",
    response_model=list[CategoryPublic],
)
async def get_categories(
    cats: CategoryServiceDep,
    pagination: PaginationDep,
    sort_by: SortBy,
    sort_order: SortOrder,
):

    return await cats.get_categories(
        pagination=pagination, sort_by=sort_by.name, sort_order=sort_order.value
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Эндпойнт для создания новой категории",
    response_model=CategoryPublic,
)
async def create_category(cats: CategoryServiceDep, category: CategoryCreate):
    return await cats.create_category(category)


@router.patch(
    "/{category_id}",
    summary="Partial update category",
    description="Эндпойнт для частичного обновления категории",
    response_model=CategoryPublic,
)
async def partial_update_category(
    cats: CategoryServiceDep, category_id: int, category: CategoryPartialUpdate
):
    try:
        return await cats.partial_update_category(category_id, category)
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException


@router.delete(
    "/{category_id}",
    summary="Delete category",
    description="Эндпойнт для логического удаления категории",
)
async def delete_category(cats: CategoryServiceDep, category_id: int) -> dict:
    try:
        return await cats.delete_category(category_id)
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException
