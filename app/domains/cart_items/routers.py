from fastapi import APIRouter, status

from app.domains.cart_items.schemas import (
    CartItemUpdate,
    CartPublic,
    CartItemPublic,
    CartItemCreate,
)
from app.domains.dependencies import DBDep, UserDep
from app.exceptions.fastapi_exceptions import (
    CartItemNotFoundHTTPException,
    ProductNotFoundHTTPException,
)
from app.exceptions.python_exceptions import (
    CartItemNotFoundException,
    ProductNotFoundException,
)


router = APIRouter(prefix="/cart", tags=["cart 🛒🛒"])


@router.get("", response_model=CartPublic)
async def get_cart(db: DBDep, current_user: UserDep):
    return await db.cart_items.get_cart(current_user.id)


@router.post(
    "/items", status_code=status.HTTP_201_CREATED, response_model=CartItemPublic
)
async def add_item_to_cart(
    db: DBDep, current_user: UserDep, create_cart_item: CartItemCreate
):
    try:
        return await db.cart_items.add_item_to_cart(
            user_id=current_user.id,
            create_cart_item=create_cart_item,
        )
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException


@router.put("/items/{product_id}", response_model=CartItemPublic)
async def update_cart_item(
    product_id: int,
    db: DBDep,
    current_user: UserDep,
    update_cart_item: CartItemUpdate,
):
    try:
        return await db.cart_items.update_cart_item(
            product_id=product_id,
            user_id=current_user.id,
            update_cart_item=update_cart_item,
        )
    except CartItemNotFoundException:
        raise CartItemNotFoundHTTPException
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(db: DBDep, current_user: UserDep, product_id: int):
    try:
        return await db.cart_items.delete_cart_item(
            user_id=current_user.id,
            product_id=product_id,
        )
    except CartItemNotFoundException:
        raise CartItemNotFoundHTTPException


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(db: DBDep, current_user: UserDep):
    return await db.cart_items.clear_cart(user_id=current_user.id)
