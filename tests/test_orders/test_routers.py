from unittest.mock import patch

from app.exceptions.python_exceptions import (
    CartIsEmptyException,
    FailedToLoadOrderException,
    OrderNotFoundException,
    ProductIsOutOfStockException,
    ProductIsUnavailableException,
    ProductWithNoPriceException,
)


async def test_checkout_order(category_user_product, authenticated_buyer):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.get("/cart")
    assert response.status_code == 200
    assert response.json()["total_quantity"] == 2

    response = await authenticated_buyer.post(
        "/orders/checkout", params={"user_id": user.id}
    )
    assert response.status_code == 201

    response = await authenticated_buyer.post(
        "/orders/checkout", params={"user_id": user.id}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cart Is Empty."


async def test_checkout_order_with_empty_cart(authenticated_buyer):

    with patch(
        "app.domains.orders.repository.OrderRepository.checkout_order"
    ) as mock_obj:
        mock_obj.side_effect = CartIsEmptyException

        response = await authenticated_buyer.post(
            "/orders/checkout", params={"user_id": 1}
        )

        assert response.status_code == 400
        mock_obj.assert_called_once()


async def test_checkout_order_with_product_unavailable(authenticated_buyer):

    with patch(
        "app.domains.orders.repository.OrderRepository.checkout_order"
    ) as mock_obj:
        mock_obj.side_effect = ProductIsUnavailableException(product_id=1)

        response = await authenticated_buyer.post(
            "/orders/checkout", params={"user_id": 1}
        )

        assert response.status_code == 400
        mock_obj.assert_called_once()


async def test_checkout_order_with_product_out_of_stock(authenticated_buyer):

    with patch(
        "app.domains.orders.repository.OrderRepository.checkout_order"
    ) as mock_obj:
        mock_obj.side_effect = ProductIsOutOfStockException(product_name="product")

        response = await authenticated_buyer.post(
            "/orders/checkout", params={"user_id": 1}
        )

        assert response.status_code == 400
        mock_obj.assert_called_once()


async def test_checkout_order_with_product_with_no_price(authenticated_buyer):

    with patch(
        "app.domains.orders.repository.OrderRepository.checkout_order"
    ) as mock_obj:
        mock_obj.side_effect = ProductWithNoPriceException(product_name="product")

        response = await authenticated_buyer.post(
            "/orders/checkout", params={"user_id": 1}
        )

        assert response.status_code == 400
        mock_obj.assert_called_once()


async def test_checkout_order_with_product_faied_to_load_order(authenticated_buyer):

    with patch(
        "app.domains.orders.repository.OrderRepository.checkout_order"
    ) as mock_obj:
        mock_obj.side_effect = FailedToLoadOrderException

        response = await authenticated_buyer.post(
            "/orders/checkout", params={"user_id": 1}
        )

        assert response.status_code == 500
        mock_obj.assert_called_once()


async def test_get_orders(category_user_product, authenticated_buyer):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.post(
        "/orders/checkout", params={"user_id": user.id}
    )
    assert response.status_code == 201

    response = await authenticated_buyer.get(
        "/orders",
        params={
            "user_id": 1,
            "page": 1,
            "page_size": 10,
        },
    )
    assert response.status_code == 200


async def test_get_order(category_user_product, authenticated_buyer):
    _, user, product = category_user_product

    response = await authenticated_buyer.post(
        "/cart/items",
        json={"product_id": product.id, "quantity": 2, "user_id": user.id},
    )

    assert response.status_code == 201

    response = await authenticated_buyer.post(
        "/orders/checkout", params={"user_id": user.id}
    )
    assert response.status_code == 201

    response = await authenticated_buyer.get(f"/orders/{1}", params={"user_id": 1})
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


async def test_get_order_with_order_not_found(authenticated_buyer):

    with patch("app.domains.orders.repository.OrderRepository.get_order") as mock_obj:
        mock_obj.side_effect = OrderNotFoundException

        response = await authenticated_buyer.get(f"/orders/{1}", params={"user_id": 1})
        assert response.status_code == 404
        mock_obj.assert_called_once()
