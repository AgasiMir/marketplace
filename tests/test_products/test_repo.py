import pytest

from app.auth import hash_password
from app.domains.products.schemas import ProductPartialUpdate, ProductPublic
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    CurrentProductSellerException,
    ProductNotFoundException,
)
from app.models import Category, User, Product
from app.uow.uow import DBManager


@pytest.fixture
async def category_user_product(db: DBManager):
    category_data = {"name": "Test Category"}
    user_data = {
        "first_name": "Test_Name",
        "last_name": "Test_Last_Name",
        "username": "Test_User",
        "email": "testuser@example.com",
        "password": hash_password("1234abcd"),
        "role": "seller",
    }

    category = Category(**category_data)
    db.add(category)
    await db.commit()

    user = User(**user_data)
    db.add(user)
    await db.commit()

    product_data = {
        "name": "Test Product",
        "description": None,
        "price": 10.00,
        "image_url": "",
        "stock": 10,
        "category_id": category.id,
        "seller_id": user.id,
    }

    product = Product(**product_data)
    db.add(product)
    await db.commit()

    return category, user, product


async def test_get_all_products(category_user_product, db: DBManager):
    res = await db.products.get_all_products(0, 10, "price")
    assert isinstance(res[0], ProductPublic)


async def test_get_products_by_category(category_user_product, db: DBManager):
    category, _, product = category_user_product

    res = await db.products.get_products_by_category(category.id)

    assert isinstance(res[0], ProductPublic)


async def test_get_products_by_non_existing_category(
    category_user_product, db: DBManager
):
    category, _, product = category_user_product

    with pytest.raises(CategoryNotFoundException):
        await db.products.get_products_by_category(1234)


async def test_get_product(category_user_product, db: DBManager):
    _, _, product = category_user_product

    res = await db.products.get_product(product.id)
    assert isinstance(res, ProductPublic)


async def test_get_non_existing_product(db: DBManager):

    with pytest.raises(ProductNotFoundException):
        await db.products.get_product(12345)


async def test_create_product(category_user_product, db: DBManager):
    category, user, _ = category_user_product
    product_data = {
        "name": "Test Product 2",
        "description": None,
        "price": 20.00,
        "image_url": "",
        "stock": 50,
        "category_id": category.id,
    }

    from app.domains.products.schemas import ProductCreate

    res = await db.products.create_product(ProductCreate(**product_data), user.id)

    assert isinstance(res, dict)
    assert res["message"] == "Product created"


async def test_create_product_with_non_existing_category(
    category_user_product, db: DBManager
):
    category, user, _ = category_user_product
    product_data = {
        "name": "Test Product 2",
        "description": None,
        "price": 20.00,
        "image_url": "",
        "stock": 50,
        "category_id": 12345,
    }

    from app.domains.products.schemas import ProductCreate

    with pytest.raises(CategoryNotFoundException):
        await db.products.create_product(ProductCreate(**product_data), user.id)


async def test_partial_update_product(category_user_product, db: DBManager):
    _, user, product = category_user_product

    data = ProductPartialUpdate(**{"name": "New Name"})

    res = await db.products.partial_update_product(product.id, data, user.id)
    assert res["message"] == "Product updated"


async def test_partial_update_non_existing_product(db: DBManager):
    with pytest.raises(ProductNotFoundException):
        await db.products.partial_update_product(12345, {"name": "New Name"}, 1)


async def test_partial_update_product_with_other_seller(
    category_user_product, db: DBManager
):
    *_, product = category_user_product
    with pytest.raises(CurrentProductSellerException):
        await db.products.partial_update_product(
            product.id, {"name": "New Name"}, 12234
        )


async def test_delete_product(category_user_product, db: DBManager):
    _, user, product = category_user_product
    res = await db.products.delete_product(product.id, user.role, user.id)
    assert res["message"] == "Product deleted"


async def test_delete_non_existing_product(db: DBManager):
    with pytest.raises(ProductNotFoundException):
        await db.products.delete_product(1234, "seller", 1)


async def test_delete_product_with_other_seller(category_user_product, db: DBManager):
    _, _, product = category_user_product
    with pytest.raises(CurrentProductSellerException):
        await db.products.delete_product(product.id, "seller", 2)
