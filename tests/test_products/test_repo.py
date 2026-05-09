import pytest


from app.domains.products.schemas import (
    ProductPartialUpdate,
    ProductPublic,
    ProductURDPublic,
)
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    CurrentProductSellerException,
    ProductNotFoundException,
)
from app.uow.uow import DBManager


async def test_get_all_products(category_user_product, db: DBManager):
    res = await db.products.get_all_products(0, 10, "price", None)
    assert isinstance(res[0], ProductPublic)


async def test_get_products_by_category(category_user_product, db: DBManager):
    category, user, product = category_user_product

    res = await db.products.get_all_products(
        0,
        10,
        "price",
        user.id,
        category.id,
    )

    assert isinstance(res[0], ProductPublic)


async def test_get_products_by_non_existing_category(
    category_user_product, db: DBManager
):
    category, _, product = category_user_product

    with pytest.raises(CategoryNotFoundException):
        await db.products.get_all_products(0, 10, "price", None, 1234)


async def test_get_product(category_user_product, db: DBManager):
    _, user, product = category_user_product

    res = await db.products.get_product(product.id, user.id)
    assert isinstance(res, ProductPublic)


async def test_get_non_existing_product(db: DBManager):

    with pytest.raises(ProductNotFoundException):
        await db.products.get_product(12345, 2)


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

    assert isinstance(res, ProductURDPublic)
    assert res.message == "Product created"


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
    assert isinstance(res, ProductURDPublic)
    assert res.message == "Product updated"


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
    assert isinstance(res, ProductURDPublic)
    assert res.message == "Product deleted"


async def test_delete_product_with_admin_role(category_user_product, db: DBManager):
    _, user, product = category_user_product
    user.role = "admin"
    res = await db.products.delete_product(product.id, user.role, user.id)
    assert isinstance(res, ProductURDPublic)
    assert res.message == "Product deleted"


async def test_delete_non_existing_product(db: DBManager):
    with pytest.raises(ProductNotFoundException):
        await db.products.delete_product(1234, "seller", 1)


async def test_delete_product_with_other_seller(category_user_product, db: DBManager):
    _, _, product = category_user_product
    with pytest.raises(CurrentProductSellerException):
        await db.products.delete_product(product.id, "seller", 2)


async def test_get_product_reviews(category_user_product, db: DBManager):
    *_, product = category_user_product
    res = await db.products.get_product_reviews(product.id)
    assert isinstance(res, list)


async def test_get_non_existing_product_reviews(db: DBManager):
    with pytest.raises(ProductNotFoundException):
        await db.products.get_product_reviews(12345)
