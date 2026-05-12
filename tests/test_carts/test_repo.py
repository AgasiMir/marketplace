import pytest
from app.domains.cart_items.schemas import (
    CartItemCreate,
    CartItemPublic,
    CartItemUpdate,
)
from app.exceptions.python_exceptions import ProductNotFoundException
from app.models.product import Product
from app.uow.uow import DBManager


async def test_get_cart(db: DBManager):
    res = await db.cart_items.get_cart(user_id=1)
    assert res


async def test_add_item_to_cart(category_user_product, db: DBManager):
    category, user, product = category_user_product

    product_data = {
        "name": "Test Product 2",
        "description": None,
        "price": 20.00,
        "image_url": "",
        "stock": 10,
        "category_id": category.id,
        "seller_id": user.id,
    }

    db_product = Product(**product_data)
    db.add(db_product)
    await db.commit()

    create_cart_item = CartItemCreate(**{"product_id": db_product.id, "quantity": 2})

    res = await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)
    assert isinstance(res, CartItemPublic)


async def test_add_item_to_cart_with_quantity_more_than_product_stock(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 12})

    res = await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)
    assert res.quantity <= product.stock


async def test_add_item_to_cart_with_product_not_found(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product

    create_cart_item = CartItemCreate(**{"product_id": 123, "quantity": 2})

    with pytest.raises(ProductNotFoundException):
        await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)


async def test_update_cart_item(category_user_product, db: DBManager):
    category, user, product = category_user_product

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})
    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)

    update_cart_item = CartItemUpdate(quantity=1)
    res = await db.cart_items.update_cart_item(
        product_id=product.id,
        update_cart_item=update_cart_item,
        user_id=user.id,
    )
    assert res.quantity == 1


async def test_update_cart_item_with_quantity_more_than_product_stock(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})
    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)

    update_cart_item = CartItemUpdate(quantity=12)
    res = await db.cart_items.update_cart_item(
        product_id=product.id,
        update_cart_item=update_cart_item,
        user_id=user.id,
    )
    assert res.quantity <= product.stock


async def test_delete_cart_item_z(category_user_product, db: DBManager):

    category, user, product = category_user_product

    create_cart_item = CartItemCreate(**{"product_id": product.id, "quantity": 2})
    await db.cart_items.add_item_to_cart(create_cart_item, user_id=user.id)

    res = await db.cart_items.delete_cart_item(product_id=product.id, user_id=user.id)
    assert res is None


async def test_clear_cart(db: DBManager):
    res = await db.cart_items.clear_cart(1)
    assert res is None
