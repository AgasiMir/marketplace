import pytest
from decimal import Decimal

from app.domains.cart_items.schemas import CartItemCreate
from app.domains.orders.schemas import OrderPublic
from app.exceptions.python_exceptions import (
    CartIsEmptyException,
    OrderNotFoundException,
    ProductIsOutOfStockException,
    ProductIsUnavailableException,
)
from app.uow.uow import DBManager


async def test_checkout_order(category_user_product, db: DBManager):
    category, user, product = category_user_product
    product.price = Decimal(f"{product.price}")
    old_stock = product.stock

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})

    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)

    res = await db.orders.checkout_order(user.id)
    assert product.stock == old_stock - create_cart_item.quantity
    assert isinstance(res, OrderPublic)


async def test_checkout_order_with_empty_cart(db: DBManager):
    with pytest.raises(CartIsEmptyException):
        await db.orders.checkout_order(1)


async def test_checkout_order_wtih_product_not_active(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product
    product.price = Decimal(f"{product.price}")

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})

    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)
    product.is_active = False
    await db.commit()

    with pytest.raises(ProductIsUnavailableException):
        await db.orders.checkout_order(user.id)


async def test_checkout_order_wtih_product_out_of_stock(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product
    product.price = Decimal(f"{product.price}")

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})

    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)
    product.stock = 0
    await db.commit()

    with pytest.raises(ProductIsOutOfStockException):
        await db.orders.checkout_order(user.id)


async def test_get_orders(db: DBManager):
    await db.orders.get_orders(page=1, page_size=10, user_id=1)


async def test_get_order(category_user_product, db: DBManager):
    category, user, product = category_user_product
    product.price = Decimal(f"{product.price}")

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})

    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)

    await db.orders.checkout_order(user.id)

    res = await db.orders.get_order(order_id=1, user_id=user.id)
    assert isinstance(res, OrderPublic)


async def test_get_non_existing_order(db: DBManager):

    with pytest.raises(OrderNotFoundException):
        await db.orders.get_order(order_id=123, user_id=123)
