import pytest
from app.auth import hash_password
from app.domains.favorites.schemas import FavoriteCreate
from app.exceptions.python_exceptions import (
    FavoriteAlreadyExistsException,
    FavoriteNotFoundException,
)
from app.models import Category, User, Product, Favorite
from app.uow.uow import DBManager


@pytest.fixture
async def category_user_product_favorite(db: DBManager):
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

    favorite = Favorite(product_id=product.id, user_id=user.id)
    db.add(favorite)
    await db.commit()

    return category, user, product, favorite


async def test_get_favorites(category_user_product_favorite, db: DBManager):
    _, user, *_ = category_user_product_favorite

    res = await db.favorites.get_favorites(user.id)
    assert len(res) == 1


async def test_add_favorite(category_user_product_favorite, db: DBManager):
    _, user, product, _ = category_user_product_favorite

    await db.favorites.delete_favorite(user.id, product.id)

    product_data = {"product_id": product.id}

    create_favorite = FavoriteCreate(**product_data)

    res = await db.favorites.add_favorite(user.id, create_favorite)
    assert res["message"] == "Favorite Added"


async def test_add_allready_existing_favorite(
    category_user_product_favorite, db: DBManager
):
    _, user, product, _ = category_user_product_favorite
    product_data = {"product_id": product.id}

    create_favorite = FavoriteCreate(**product_data)

    with pytest.raises(FavoriteAlreadyExistsException):
        await db.favorites.add_favorite(user.id, create_favorite)


async def test_delete_favorite(category_user_product_favorite, db: DBManager):
    _, user, product, _ = category_user_product_favorite
    res = await db.favorites.delete_favorite(user.id, product.id)
    assert res["message"] == "Favorite deleted"


async def test_delete_non_existing_favorite(db: DBManager):
    with pytest.raises(FavoriteNotFoundException):
        await db.favorites.delete_favorite(1234, 5678)
