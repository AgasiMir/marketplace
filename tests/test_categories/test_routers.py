import pytest
from unittest.mock import patch


from app.exceptions.python_exceptions import (
    CategoryNotFoundException,
    WrongSortByException,
)


@pytest.fixture
async def create_category(authenticated_admin):
    response = await authenticated_admin.post(
        "/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 201
    return response.json()


async def test_get_categories(async_client):
    response = await async_client.get(
        "/categories",
        params={
            "page": 1,
            "page_size": 10,
            "sort_by": "name",
            "sort_order": "asc",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) <= 10


async def test_get_categories_with_2nd_page(async_client):
    response = await async_client.get(
        "/categories",
        params={
            "page": 2,
            "page_size": 10,
            "sort_by": "name",
            "sort_order": "asc",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_get_categories_with_worng_sort_by_data(async_client):

    with patch(
        "app.domains.categories.service.CategoryService.get_categories"
    ) as mock_obj:
        mock_obj.side_effect = WrongSortByException

        response = await async_client.get(
            "/categories",
            params={
                "page": 1,
                "page_size": 10,
                "sort_by": "name",
                "sort_order": "asc",
            },
        )
        assert response.status_code == 400
        mock_obj.assert_awaited_once()


async def test_create_category(authenticated_admin):
    response = await authenticated_admin.post(
        "/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == "Test Category"


async def test_create_category_without_permission(authenticated_buyer):
    response = await authenticated_buyer.post(
        "/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 403


async def test_partial_update_category(create_category, authenticated_admin):

    response = await authenticated_admin.patch(
        f"/categories/{create_category['id']}",
        json={"name": "Updated Test Category"},
    )
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == "Updated Test Category"


async def test_partial_update_category_without_permission(
    create_category, authenticated_buyer
):

    response = await authenticated_buyer.patch(
        f"/categories/{create_category['id']}",
        json={"name": "Updated Test Category"},
    )

    assert response.status_code == 403


async def test_partial_update_non_existing_category(authenticated_admin):
    with patch(
        "app.domains.categories.service.CategoryService.partial_update_category"
    ) as mock_category:
        mock_category.side_effect = CategoryNotFoundException

        response = await authenticated_admin.patch(
            "/categories/1",
            json={"name": "Updated Test Category"},
        )
        assert response.status_code == 404
        mock_category.assert_called_once()


async def test_delete_category(create_category, authenticated_admin):

    response = await authenticated_admin.delete(
        f"/categories/{create_category['id']}",
    )
    assert response.json() == {"message": "Category deleted"}


async def test_delete_non_existing_category(authenticated_admin):
    with patch(
        "app.domains.categories.service.CategoryService.delete_category"
    ) as mock_category:
        mock_category.side_effect = CategoryNotFoundException

        response = await authenticated_admin.delete(
            "/categories/1",
        )
        assert response.status_code == 404
        mock_category.assert_called_once_with(1)


async def test_delete_category_without_permission(create_category, authenticated_buyer):

    response = await authenticated_buyer.delete(
        f"/categories/{create_category['id']}",
    )
    assert response.status_code == 403


async def test_delete_category_without_login(async_client):

    response = await async_client.delete("/categories/123")
    assert response.status_code == 401
