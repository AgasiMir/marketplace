from fastapi import APIRouter, Body, Depends, status
from app.cache_key_builders import key_builder_for_lists, product_key_builder
from app.domains.products.schemas import (
    ProductAdminDeletePublic,
    ProductCreate,
    ProductPartialUpdate,
    ProductPublic,
    ProductURDPublic,
)
from app.domains.dependencies import (
    OptionalUserDep,
    PaginationDep,
    FiltersDep,
    ProductServiceDep,
    SellerDep,
    UserDep,
)

from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

from app.domains.reviews.schemas import ReviewPublic
from app.exceptions.fastapi_exceptions import (
    CategoryNotFoundHTTPException,
    CurrentProductSellerHTTPException,
    MinPriceMustBeLessThanMaxPriceHTTPException,
    NotEnoughRightsHTTPException,
    ProductNotFoundHTTPException,
    WrongSortByHTTPException,
)
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    CurrentProductSellerException,
    MinPriceMustBeLessThanMaxPriceException,
    NotEnoughRightsException,
    ProductNotFoundException,
    WrongSortByException,
)
from app.utils.utils import ProductSortBy, SortOrder
from fastapi_cache.decorator import cache


router = APIRouter(
    prefix="/products",
    tags=["products 🛒🛒"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(10, Duration.SECOND * 2))))],
)


@router.get(
    "",
    summary="Get all products",
    description="Эндпойнт для получения всех товаров",
    response_model=list[ProductPublic],
)
@cache(expire=30, namespace="list_of_products", key_builder=key_builder_for_lists)
async def get_products(
    products: ProductServiceDep,
    pagination: PaginationDep,
    filters: FiltersDep,
    sort_by: ProductSortBy,
    sort_order: SortOrder,
    current_user: OptionalUserDep,
):
    user_id = current_user.id if current_user else None
    try:
        return await products.get_all_products(
            pagination=pagination,
            filters=filters,
            sort_by=sort_by.name,
            sort_order=sort_order.value,
            user_id=user_id,
        )
    except WrongSortByException:
        raise WrongSortByHTTPException
    except MinPriceMustBeLessThanMaxPriceException:
        raise MinPriceMustBeLessThanMaxPriceHTTPException


@router.get(
    "/{product_id}",
    summary="Get product by id",
    description="Эндпойнт для получения товара по id",
    response_model=ProductPublic,
)
@cache(expire=300, namespace="product", key_builder=product_key_builder)
async def get_product(
    product_id: int,
    products: ProductServiceDep,
    current_user: OptionalUserDep,
):
    user_id = current_user.id if current_user else None
    try:
        return await products.get_product(product_id, user_id)
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException


@router.get(
    "/category/{category_id}",
    summary="Get products by category",
    description="Эндпойнт для получения товаров по категории",
    response_model=list[ProductPublic],
)
@cache(expire=30, namespace="list_of_products", key_builder=key_builder_for_lists)
async def get_products_by_category(
    category_id: int,
    pagination: PaginationDep,
    filters: FiltersDep,
    sort_by: ProductSortBy,
    sort_order: SortOrder,
    products: ProductServiceDep,
    current_user: OptionalUserDep,
):
    user_id = current_user.id if current_user else None
    try:
        return await products.get_all_products(
            category_id=category_id,
            user_id=user_id,
            pagination=pagination,
            filters=filters,
            sort_by=sort_by.name,
            sort_order=sort_order.value,
        )
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException
    except MinPriceMustBeLessThanMaxPriceException:
        raise MinPriceMustBeLessThanMaxPriceHTTPException


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Эндпойнт для создания товара. Доступен только продавцу",
    response_model=ProductURDPublic,
)
async def create_product(
    current_seller: SellerDep,
    products: ProductServiceDep,
    create_product: ProductCreate = Body(
        openapi_examples={
            "1": {
                "summary": "The Best Product",
                "value": {
                    "name": "The Best Product",
                    "description": "The Best Product Description",
                    "price": 100500,
                    "image_url": "",
                    "stock": 1,
                    "category_id": 1,
                },
            }
        }
    ),
) -> dict:
    try:
        return await products.create_product(
            create_product,
            seller_id=current_seller.id,
            email=current_seller.email,
            username=current_seller.username,
        )
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException


@router.patch(
    "/{product_id}",
    summary="Partial update product",
    description="Эндпойнт для частичного обновления товара. Доступен только продавцу",
    response_model=ProductURDPublic,
)
async def partial_update_product(
    current_seller: SellerDep,
    products: ProductServiceDep,
    product_id: int,
    patch_product: ProductPartialUpdate,
) -> dict:
    try:
        return await products.partial_update_product(
            product_id=product_id,
            patch_product=patch_product,
            seller_id=current_seller.id,
            email=current_seller.email,
            username=current_seller.username,
        )
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    except CurrentProductSellerException:
        raise CurrentProductSellerHTTPException


@router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Эндпойнт для удаления товара. Доступен только продавцу или администратору",
    response_model=ProductURDPublic | ProductAdminDeletePublic,
)
async def delete_product(
    product_id: int,
    products: ProductServiceDep,
    current_user: UserDep,
) -> dict:
    try:
        return await products.delete_product(
            product_id=product_id,
            user_id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            user_role=current_user.role,
        )
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    except NotEnoughRightsException:
        raise NotEnoughRightsHTTPException
    except CurrentProductSellerException:
        raise CurrentProductSellerHTTPException


@router.get("/{product_id}/reviews", response_model=list[ReviewPublic])
async def get_product_reviews(product_id: int, products: ProductServiceDep):
    try:
        return await products.get_product_reviews(product_id=product_id)
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
