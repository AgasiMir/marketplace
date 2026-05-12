from unittest.mock import patch

from app.exceptions.python_exceptions import (
    CartItemNotFoundException,
    ProductNotFoundException,
)
from app.models.product import Product
from app.uow.uow import DBManager


async def test_get_cart(category_user_product, authenticated_buyer):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.get("/cart")
    assert response.status_code == 200
    assert response.json()["total_quantity"] == 2


async def test_get_cart_without_auth(category_user_product, async_client):

    response = await async_client.get("/cart")
    assert response.status_code == 401


async def test_add_non_existing_item_to_cart(
    category_user_product, authenticated_buyer
):
    _, user, _ = category_user_product

    with patch(
        "app.domains.cart_items.repository.CartItemsRepository.add_item_to_cart"
    ) as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        response = await authenticated_buyer.post(
            "/cart/items",
            json={"product_id": 1234, "quantity": 2, "user_id": user.id},
        )
        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_add_item_to_cart_wtihout_auth(category_user_product, async_client):
    _, user, _ = category_user_product

    response = await async_client.post(
        "/cart/items",
        json={"product_id": 1234, "quantity": 2, "user_id": user.id},
    )
    assert response.status_code == 401


async def test_add_item_to_cart_wtih_wrong_params(
    category_user_product, authenticated_buyer
):
    _, user, _ = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": 1234, "user_id": user.id},
    )
    assert response.status_code == 422


async def test_add_negative_amount_of_items_to_cart(
    category_user_product, authenticated_buyer
):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": -8, "user_id": user.id},
    )
    assert response.status_code == 422


async def test_add_no_more_than_stock_amount_of_items_to_cart(
    category_user_product, authenticated_buyer
):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 8, "user_id": user.id},
    )
    assert response.status_code == 201
    assert response.json()["quantity"] == 8

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 7, "user_id": user.id},
    )

    assert response.status_code == 201
    assert response.json()["quantity"] == product.stock


async def test_update_cart_item(category_user_product, authenticated_buyer):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.put(
        f"/cart/items/{product.id}",
        json={
            "quantity": 3,
            "user_id": user.id,
        },
    )
    assert response.json()["quantity"] == 3


async def test_update_cart_item_with_negative_quantity(
    category_user_product, authenticated_buyer
):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.put(
        f"/cart/items/{product.id}",
        json={
            "quantity": -3,
            "user_id": user.id,
        },
    )
    assert response.status_code == 422


async def test_update_cart_item_with_quantity_more_than_product_stock(
    category_user_product, authenticated_buyer
):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.put(
        f"/cart/items/{product.id}",
        json={
            "quantity": 15,
            "user_id": user.id,
        },
    )
    assert response.json()["quantity"] <= product.stock


async def test_update_cart_item_with_product_not_found(
    category_user_product, authenticated_buyer
):
    _, user, _ = category_user_product

    with patch(
        "app.domains.cart_items.repository.CartItemsRepository.update_cart_item"
    ) as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        response = await authenticated_buyer.put(
            f"/cart/items/{1234}",
            json={
                "quantity": 3,
                "user_id": user.id,
            },
        )
        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_update_cart_item_with_cart_item_not_found(
    category_user_product, authenticated_buyer
):
    _, user, _ = category_user_product

    with patch(
        "app.domains.cart_items.repository.CartItemsRepository.update_cart_item"
    ) as mock_obj:
        mock_obj.side_effect = CartItemNotFoundException

        response = await authenticated_buyer.put(
            f"/cart/items/{1234}",
            json={
                "quantity": 3,
                "user_id": user.id,
            },
        )
        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_delete_cart_item(category_user_product, authenticated_buyer):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.delete(
        f"/cart/items/{product.id}",
        params={"user_id": user.id},
    )

    assert response.status_code == 204


async def test_delete_cart_item_with_cart_item_not_found(
    category_user_product, authenticated_buyer
):
    with patch(
        "app.domains.cart_items.repository.CartItemsRepository.delete_cart_item"
    ) as mock_obj:
        mock_obj.side_effect = CartItemNotFoundException

        response = await authenticated_buyer.delete(
            f"/cart/items/{1234}",
            params={"user_id": 5678},
        )

        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_clear_cart(category_user_product, authenticated_buyer, db: DBManager):
    category, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

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

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": db_product.id, "quantity": 1, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.get("/cart")
    assert response.status_code == 200
    assert response.json()["total_quantity"] == 3

    response = await authenticated_buyer.delete(
        "/cart",
        params={"user_id": user.id},
    )
    assert response.status_code == 204
