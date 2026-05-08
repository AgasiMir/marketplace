import pytest
from app.auth import hash_password
from app.domains.products.service import ProductService
from app.domains.products.schemas import (
    ProductCreate,
    ProductURDPublic,
    ProductPartialUpdate,
)
from app.exceptions.python_exceptions import NotEnoughRightsException
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


async def test_create_product_service(category_user_product, db: DBManager):
    category, user, _ = category_user_product
    product_data = {
        "name": "Test Product 3",
        "description": None,
        "price": 30.00,
        "image_url": "",
        "stock": 30,
        "category_id": category.id,
        "seller_id": user.id,
    }
    create_product = ProductCreate(**product_data)
    product_service = ProductService(db)

    res = await product_service.create_product(
        create_product,
        user.id,
        email=user.email,
        username=user.username,
    )
    assert isinstance(res, ProductURDPublic)


async def test_partial_update_product_service(category_user_product, db: DBManager):
    category, user, product = category_user_product
    partial_update = {"price": 37.00}
    update_product = ProductPartialUpdate(**partial_update)
    product_service = ProductService(db)

    res = await product_service.partial_update_product(
        product.id,
        update_product,
        user.id,
        user.email,
        user.username,
    )
    assert isinstance(res, ProductURDPublic)


async def test_delete_product_service_with_seller_role(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product

    product_service = ProductService(db)
    res = await product_service.delete_product(
        product.id,
        user.id,
        user.email,
        user.username,
        user.role,
    )
    assert isinstance(res, ProductURDPublic)


async def test_delete_product_service_with_admin_role(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product
    user.role = "admin"

    product_service = ProductService(db)
    res = await product_service.delete_product(
        product.id,
        user.id,
        user.email,
        user.username,
        user.role,
    )
    assert isinstance(res, ProductURDPublic)


async def test_delete_product_service_with_buyer_role(
    category_user_product, db: DBManager
):
    category, user, product = category_user_product
    user.role = "buyer"

    product_service = ProductService(db)
    with pytest.raises(NotEnoughRightsException):
        await product_service.delete_product(
            product.id, user.id, user.email, user.username, user.role
        )
