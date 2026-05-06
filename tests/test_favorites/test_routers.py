import pytest

from unittest.mock import patch
from app.auth import hash_password
from app.exceptions.python_exceptions import (
    FavoriteAlreadyExistsException,
    FavoriteLimitExceededException,
    FavoriteNotFoundException,
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

    return category, product


async def test_get_favorites(category_user_product, authenticated_buyer):
    *_, product = category_user_product
    response = await authenticated_buyer.post(
        "/favorites",
        json={"product_id": product.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.get("/favorites")
    assert response.status_code == 200


async def test_get_favorites_without_auth(async_client):

    response = await async_client.get("/favorites")
    assert response.status_code == 401


async def test_add_favorite(category_user_product, authenticated_buyer):
    *_, product = category_user_product

    response = await authenticated_buyer.post(
        "/favorites",
        json={"product_id": product.id},
    )

    assert response.status_code == 201


async def test_add_favorite_without_auth(async_client):

    response = await async_client.post(
        "/favorites",
        json={"product_id": 1},
    )

    assert response.status_code == 401


async def test_add_favorite_without_wrong_type_id(authenticated_buyer):

    response = await authenticated_buyer.delete("/favorites/abcde")
    assert response.status_code == 422


async def test_add_already_exists_favorite(authenticated_buyer):

    with patch(
        "app.domains.favorites.repository.FavoriteRepository.add_favorite"
    ) as mock_obj:
        mock_obj.side_effect = FavoriteAlreadyExistsException

        response = await authenticated_buyer.post(
            "/favorites",
            json={"product_id": 1},
        )

        assert response.status_code == 409
        mock_obj.assert_called_once()


async def test_add_non_existing_product_to_favorite(authenticated_buyer):

    with patch(
        "app.domains.favorites.repository.FavoriteRepository.add_favorite"
    ) as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        response = await authenticated_buyer.post(
            "/favorites",
            json={"product_id": 1},
        )

        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_add_favorite_with_limit_exceeded(authenticated_buyer):

    with patch(
        "app.domains.favorites.repository.FavoriteRepository.add_favorite"
    ) as mock_obj:
        mock_obj.side_effect = FavoriteLimitExceededException

        response = await authenticated_buyer.post(
            "/favorites",
            json={"product_id": 1},
        )

        assert response.status_code == 400
        mock_obj.assert_called_once()


async def test_delete_favorite(category_user_product, authenticated_buyer):
    *_, product = category_user_product
    response = await authenticated_buyer.post(
        "/favorites",
        json={"product_id": product.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.delete(f"/favorites/{product.id}")
    assert response.json() == {"message": "Favorite deleted"}


async def test_delete_favorite_without_auth(async_client):

    response = await async_client.delete(f"/favorites/{1}")
    assert response.status_code == 401


async def test_delete_favorite_without_wrong_type_id(authenticated_buyer):

    response = await authenticated_buyer.delete("/favorites/[1]")
    assert response.status_code == 422


async def test_delete_non_existing_favorite(authenticated_buyer):

    with patch(
        "app.domains.favorites.repository.FavoriteRepository.delete_favorite"
    ) as mock_obj:
        mock_obj.side_effect = FavoriteNotFoundException

        response = await authenticated_buyer.delete(f"/favorites/{123}")
        assert response.status_code == 404
        mock_obj.assert_called_once()
