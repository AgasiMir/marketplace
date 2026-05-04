from unittest.mock import patch

from app.exceptions.python_exceptions import CategoryNotFoundException


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


async def test_create_category(authenticated_admin):
    response = await authenticated_admin.post(
        "/categories",
        json={"name": "Test Category"},
    )
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == "Test Category"


async def test_partial_update_category(authenticated_admin):
    res = await authenticated_admin.post(
        "/categories",
        json={"name": "Test Category"},
    )

    response = await authenticated_admin.patch(
        f"/categories/{res.json()['id']}",
        json={"name": "Updated Test Category"},
    )
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == "Updated Test Category"


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


async def test_delete_category(authenticated_admin):

    res = await authenticated_admin.post(
        "/categories",
        json={"name": "Test Category"},
    )

    response = await authenticated_admin.delete(
        f"/categories/{res.json()['id']}",
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
