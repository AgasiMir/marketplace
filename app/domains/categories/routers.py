from fastapi import APIRouter, Depends, status

from app.cache_key_builders import key_builder_for_lists
from app.domains.categories.schemas import (
    CategoryCreate,
    CategoryPartialUpdate,
    CategoryPublic,
)
from app.domains.dependencies import CategoryServiceDep, PaginationDep, AdminDep
from app.utils.utils import SortBy, SortOrder


from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter


from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    WrongSortByException,
)
from app.exceptions.fastapi_exceptions import (
    CategoryNotFoundHTTPException,
    WrongSortByHTTPException,
)

from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/categories",
    tags=["categories 📁📁"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.SECOND * 2))))],
)


@router.get(
    "",
    summary="Get categories",
    description="Эндпойнт для получения категорий",
    response_model=list[CategoryPublic],
)
@cache(expire=300, namespace="category_list", key_builder=key_builder_for_lists)
async def get_categories(
    cats: CategoryServiceDep,
    pagination: PaginationDep,
    sort_by: SortBy,
    sort_order: SortOrder,
):
    try:
        return await cats.get_categories(
            pagination=pagination,
            sort_by=sort_by.name,
            sort_order=sort_order.value,
        )
    except WrongSortByException:
        raise WrongSortByHTTPException


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Эндпойнт для создания новой категории. Доступен только администратору",
    response_model=CategoryPublic,
)
async def create_category(
    cats: CategoryServiceDep, create_category: CategoryCreate, admin: AdminDep
):
    return await cats.create_category(create_category)


@router.patch(
    "/{category_id}",
    summary="Partial update category",
    description="Эндпойнт для частичного обновления категории. Доступен только администратору",
    response_model=CategoryPublic,
)
async def partial_update_category(
    admin: AdminDep,
    cats: CategoryServiceDep,
    category_id: int,
    patch_category: CategoryPartialUpdate,
):
    try:
        return await cats.partial_update_category(category_id, patch_category)
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException


@router.delete(
    "/{category_id}",
    summary="Delete category",
    description="Эндпойнт для логического удаления категории. Доступен только администратору",
)
async def delete_category(
    cats: CategoryServiceDep, category_id: int, admin: AdminDep
) -> dict:
    try:
        return await cats.delete_category(category_id)
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException
