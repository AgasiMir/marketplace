from fastapi import APIRouter, Body, status
from app.domains.products.schemas import (
    ProductCreate,
    ProductPartialUpdate,
    ProductPublic,
)
from app.domains.dependencies import PaginationDep, ProductServiceDep
from app.exceptions.fastapi_exceptions import (
    CategoryNotFoundHTTPException,
    ProductNotFoundHTTPException,
    WrongSortByHTTPException,
)
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    ProductNotFoundException,
    WrongSortByException,
)
from app.utils.utils import ProductSortBy, SortOrder


router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "",
    summary="Get all products",
    description="Эндпойнт для получения всех товаров",
    response_model=list[ProductPublic],
)
async def get_products(
    products: ProductServiceDep,
    pagination: PaginationDep,
    sort_by: ProductSortBy,
    sort_order: SortOrder,
):
    try:
        return await products.get_all_products(
            pagination=pagination,
            sort_by=sort_by.name,
            sort_order=sort_order.value,
        )
    except WrongSortByException:
        raise WrongSortByHTTPException


@router.get(
    "/{product_id}",
    summary="Get product by id",
    description="Эндпойнт для получения товара по id",
    response_model=ProductPublic,
)
async def get_product(product_id: int, products: ProductServiceDep):
    try:
        return await products.get_product(product_id)
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException


@router.get(
    "/category/{category_id}",
    summary="Get products by category",
    description="Эндпойнт для получения товаров по категории",
    response_model=list[ProductPublic],
)
async def get_products_by_category(category_id: int, products: ProductServiceDep):
    try:
        return await products.get_products_by_category(category_id)
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Эндпойнт для создания товара. Доступен только продавцу",
    response_model=ProductPublic,
)
async def create_product(
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
):
    try:
        return await products.create_product(create_product)
    except CategoryNotFoundException:
        raise CategoryNotFoundHTTPException


@router.patch(
    "",
    summary="Partial update product",
    description="Эндпойнт для частичного обновления товара. Доступен только продавцу",
    response_model=ProductPublic,
)
async def partial_update_product(
    products: ProductServiceDep,
    product_id: int,
    patch_product: ProductPartialUpdate,
):
    try:
        return await products.partial_update_product(product_id, patch_product)
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException


@router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Эндпойнт для удаления товара. Доступен только продавцу или администратору",
)
async def delete_product(product_id: int, products: ProductServiceDep) -> dict:
    try:
        return await products.delete_product(product_id)
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
