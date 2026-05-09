from unittest.mock import patch

from asyncpg import NotNullViolationError

from app.exceptions.python_exceptions import (
    OnlyAuthorOrAdminCanDeleteReviewException,
    ProductNotFoundException,
    ReviewNotFoundException,
)


async def test_create_product_review(category_user_product, authenticated_buyer):
    response = await authenticated_buyer.post(
        "/reviews",
        json={"product_id": 1, "comment": "Nice", "grade": 4},
    )
    assert response.status_code == 201
    assert response.json()["comment"] == "Nice"


async def test_create_non_existing_product_review(authenticated_buyer):

    with patch("app.domains.reviews.service.ReviewService.create_review") as mock_obj:
        mock_obj.side_effect = ProductNotFoundException

        response = await authenticated_buyer.post(
            "/reviews",
            json={"product_id": 1, "comment": "Nice", "grade": 4},
        )
        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_create_product_review_with_null_grade(authenticated_buyer):

    with patch("app.domains.reviews.service.ReviewService.create_review") as mock_obj:
        mock_obj.side_effect = NotNullViolationError

        response = await authenticated_buyer.post(
            "/reviews",
            json={"product_id": 1, "comment": "Nice", "grade": 4},
        )
        assert response.status_code == 400
        mock_obj.assert_called_once()


async def test_create_product_review_without_permission(async_client):
    response = await async_client.post(
        "/reviews",
        json={"product_id": 1, "comment": "Nice", "grade": 4},
    )
    assert response.status_code == 401


async def test_delete_product_review_with_author(
    category_user_product, authenticated_buyer
):
    response = await authenticated_buyer.post(
        "/reviews",
        json={"product_id": 1, "comment": "Nice", "grade": 4},
    )
    assert response.status_code == 201

    response = await authenticated_buyer.delete("/reviews/1")
    assert response.json()["message"] == "Review Deleted"


async def test_delete_product_review_with_admin(
    category_user_product, authenticated_buyer, authenticated_admin
):
    *_, product = category_user_product
    response = await authenticated_buyer.post(
        "/reviews",
        json={"product_id": 1, "comment": "Nice", "grade": 4},
    )
    assert response.status_code == 201
    assert response.json()["grade"] == 4

    response = await authenticated_admin.delete("/reviews/1")
    assert response.json()["message"] == "Review Deleted"


async def test_delete_product_non_existing_review(authenticated_buyer):

    with patch("app.domains.reviews.service.ReviewService.delete_review") as mock_obj:
        mock_obj.side_effect = ReviewNotFoundException

        response = await authenticated_buyer.delete("/reviews/1")
        assert response.status_code == 404
        mock_obj.assert_called_once()


async def test_delete_product_review_with_not_enough_rights(authenticated_buyer):

    with patch("app.domains.reviews.service.ReviewService.delete_review") as mock_obj:
        mock_obj.side_effect = OnlyAuthorOrAdminCanDeleteReviewException

        response = await authenticated_buyer.delete("/reviews/1")
        assert response.status_code == 403
        mock_obj.assert_called_once()


async def test_product_rating(category_user_product, authenticated_buyer):
    *_, product = category_user_product
    response = await authenticated_buyer.post(
        "/reviews",
        json={"product_id": 1, "comment": "Nice", "grade": 4},
    )
    assert response.status_code == 201
    assert response.json()["grade"] == 4

    response = await authenticated_buyer.get("/products/1")
    assert response.json()["rating"] == 4
