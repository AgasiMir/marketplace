from unittest.mock import patch
from app.auth import create_access_token
from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    CurrentProductSellerException,
    NotEnoughRightsException,
    ProductNotFoundException,
    WrongSortByException,
)


async def test_get_all_products(category_user_product, async_client):
    res = await async_client.get(
        "/products",
        params={"sort_by": "price", "sort_order": "desc", "page": 1, "page_size": 10},
    )

    assert res.status_code == 200
    assert len(res.json()) == 1


async def test_get_all_products_with_2nd_page(category_user_product, async_client):
    res = await async_client.get(
        "/products",
        params={"sort_by": "price", "sort_order": "desc", "page": 2, "page_size": 10},
    )

    assert res.status_code == 200
    assert len(res.json()) == 0


async def test_get_all_products_with_worng_sortby_data(
    category_user_product, async_client
):

    with patch(
        "app.domains.products.service.ProductService.get_all_products"
    ) as mock_obj:
        mock_obj.side_effect = WrongSortByException

        res = await async_client.get(
            "/products",
            params={
                "sort_by": "price",
                "sort_order": "desc",
                "page": 1,
                "page_size": 10,
            },
        )

        assert res.status_code == 400
        mock_obj.assert_called_once()


async def test_get_all_products_with_inactive_category(
    category_user_product, async_client, db
):
    category, *_ = category_user_product

    category.is_active = False
    await db.commit()

    res = await async_client.get(
        "/products",
        params={"sort_by": "price", "sort_order": "desc", "page": 1, "page_size": 10},
    )

    assert res.status_code == 200
    assert len(res.json()) == 0


async def test_get_product_by_id(category_user_product, async_client):
    *_, product = category_user_product
    res = await async_client.get(f"/products/{product.id}")

    assert res.status_code == 200


async def test_get_product_by_id_with_str_id(async_client):

    res = await async_client.get("/products/one")
    assert res.status_code == 422


async def test_get_non_existing_product_by_id(async_client):
    with patch("app.domains.products.service.ProductService.get_product") as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        res = await async_client.get("/products/123")

        assert res.status_code == 404
        mock_obj.assert_called_once()


async def test_get_product_by_id_with_inactive_user(
    category_user_product, async_client, db
):
    _, user, product = category_user_product

    user.is_active = False
    await db.commit()

    res = await async_client.get(f"/products/{product.id}")

    assert res.status_code == 404


async def test_get_products_by_category(category_user_product, async_client):
    category, *_ = category_user_product
    res = await async_client.get(
        f"/products/category/{category.id}",
        params={
            "sort_by": "price",
            "sort_order": "desc",
            "page": 1,
            "page_size": 10,
        },
    )

    assert res.status_code == 200


async def test_get_products_by_category_with_inactive_product(
    category_user_product, async_client, db
):
    category, _, product = category_user_product

    product.is_active = 0
    await db.commit()

    res = await async_client.get(
        f"/products/category/{category.id}",
        params={
            "sort_by": "price",
            "sort_order": "desc",
            "page": 1,
            "page_size": 10,
        },
    )

    assert res.status_code == 200
    assert len(res.json()) == 0


async def test_get_products_by_non_existing_category(async_client):

    with patch(
        "app.domains.products.service.ProductService.get_all_products"
    ) as mock_obj:
        mock_obj.side_effect = CategoryNotFoundException

        res = await async_client.get(
            f"/products/category/{123}",
            params={
                "sort_by": "price",
                "sort_order": "desc",
                "page": 1,
                "page_size": 10,
            },
        )

        assert res.status_code == 404
        mock_obj.assert_called_once()


async def test_create_product(category_user_product, authenticated_seller):
    category, user, _ = category_user_product
    product_data = {
        "name": "Test Product 2",
        "description": None,
        "price": 10.00,
        "image_url": "",
        "stock": 10,
        "category_id": category.id,
        "seller_id": user.id,
    }

    res = await authenticated_seller.post("/products", json=product_data)

    assert res.status_code == 201


async def test_create_product_for_non_existing_category(authenticated_seller):

    product_data = {
        "name": "Test Product 2",
        "description": None,
        "price": 10.00,
        "image_url": "",
        "stock": 10,
        "category_id": 123,
        "seller_id": 1,
    }

    with patch(
        "app.domains.products.service.ProductService.create_product"
    ) as mock_obj:
        mock_obj.side_effect = CategoryNotFoundException

        res = await authenticated_seller.post("/products", json=product_data)

        assert res.status_code == 404
        mock_obj.assert_called_once()


async def test_create_product_without_permission(
    category_user_product, authenticated_buyer
):
    category, user, _ = category_user_product
    product_data = {
        "name": "Test Product 2",
        "description": None,
        "price": 10.00,
        "image_url": "",
        "stock": 10,
        "category_id": 123,
        "seller_id": user.id,
    }

    res = await authenticated_buyer.post("/products", json=product_data)

    assert res.status_code == 403


async def test_partial_update_product(category_user_product, async_client):
    _, user, product = category_user_product
    partial_data = {"price": 8.00}

    token = create_access_token(
        data={
            "sub": user.username,
            "id": user.id,
            "role": f"{user.role}",
        }
    )

    res = await async_client.patch(
        f"/products/{product.id}",
        json=partial_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200


async def test_partial_update_non_existing_product(category_user_product, async_client):
    _, user, product = category_user_product
    partial_data = {"price": 8.00}

    token = create_access_token(
        data={
            "sub": user.username,
            "id": user.id,
            "role": f"{user.role}",
        }
    )

    with patch(
        "app.domains.products.service.ProductService.partial_update_product"
    ) as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        res = await async_client.patch(
            f"/products/{12345}",
            json=partial_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert res.status_code == 404
        mock_obj.assert_called_once()


async def test_partial_update_with_other_seller(
    category_user_product, authenticated_seller
):
    *_, product = category_user_product
    partial_data = {"price": 8.00}

    with patch(
        "app.domains.products.service.ProductService.partial_update_product"
    ) as mock_obj:
        mock_obj.side_effect = CurrentProductSellerException

        res = await authenticated_seller.patch(
            f"/products/{product.id}",
            json=partial_data,
        )

        assert res.status_code == 403
        mock_obj.assert_called_once()


async def test_delete_product_by_admin(category_user_product, authenticated_admin):
    _, _, product = category_user_product

    res = await authenticated_admin.delete(f"/products/{product.id}")
    assert res.status_code == 200


async def test_delete_non_existing_product(authenticated_admin):
    with patch(
        "app.domains.products.service.ProductService.delete_product"
    ) as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        res = await authenticated_admin.delete(f"/products/{123}")
        assert res.status_code == 404
        mock_obj.assert_called_once()


async def test_delete_product_with_not_enough_rights(authenticated_admin):
    with patch(
        "app.domains.products.service.ProductService.delete_product"
    ) as mock_obj:
        mock_obj.side_effect = NotEnoughRightsException

        res = await authenticated_admin.delete(f"/products/{123}")
        assert res.status_code == 403
        mock_obj.assert_called_once()


async def test_delete_product_with_other_seller(authenticated_seller):
    with patch(
        "app.domains.products.service.ProductService.delete_product"
    ) as mock_obj:
        mock_obj.side_effect = CurrentProductSellerException

        res = await authenticated_seller.delete(f"/products/{123}")
        assert res.status_code == 403
        mock_obj.assert_called_once()


async def test_get_product_reviews(category_user_product, async_client):
    _, _, product = category_user_product
    res = await async_client.get(f"/products/{product.id}/reviews")
    assert res.status_code == 200


async def test_get_product_reviews_for_non_existing_product(async_client):

    with patch(
        "app.domains.products.service.ProductService.get_product_reviews"
    ) as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        res = await async_client.get(f"/products/{1234}/reviews")
        assert res.status_code == 404
        mock_obj.assert_called_once()
