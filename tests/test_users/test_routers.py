from unittest.mock import patch

import pytest
from app.auth import create_access_token
from app.exceptions.python_exceptions import (
    IncorrectCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)

from app.models.user import User
from app.uow.uow import DBManager

data = {
    "first_name": "John",
    "last_name": "Doe",
    "username": "JD",
    "email": "user@example.com",
    "password": "1234abcd",
    "role": "buyer",
}


@pytest.fixture
async def admin_user(db: DBManager):

    admin_user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": "1234abcd",
        "role": "admin",
    }

    admin_user = User(**admin_user_data)
    db.add(admin_user)
    await db.commit()

    token = create_access_token(
        data={
            "sub": admin_user.username,
            "id": admin_user.id,
            "role": f"{admin_user.role}",
        }
    )

    return token


async def test_get_user_profile(authenticated_buyer):
    response = await authenticated_buyer.get("/users/me")
    assert response.status_code == 200


async def test_create_user(async_client):
    response = await async_client.post("/users", json=data)
    assert response.status_code == 201


async def test_create_already_existing_user(async_client):
    await async_client.post("/users", json=data)

    with patch("app.domains.users.service.UserService.create_user") as mock_obj:
        mock_obj.side_effect = UserAlreadyExistsException

        response = await async_client.post("/users", json=data)

        assert response.status_code == 409
        mock_obj.assert_called_once()


async def test_login(authenticated_buyer):
    res = await authenticated_buyer.post(
        "/users/login",
        data={"username": "JD", "password": "1234abcd"},
    )

    assert res.status_code == 200
    print(res.json()["refresh_token"])


async def test_login_with_wrong_credentials(async_client):
    with patch("app.domains.users.service.UserService.login") as mock_obj:
        mock_obj.side_effect = IncorrectCredentialsException

        res = await async_client.post(
            "/users/login",
            data={"username": "JDDD", "password": "1234abcd"},
        )

        assert res.status_code == 401
        mock_obj.assert_called_once()


async def test_refresh_token(authenticated_buyer):
    res = await authenticated_buyer.post(
        "/users/login",
        data={"username": "JD", "password": "1234abcd"},
    )

    refresh_token = res.json()["refresh_token"]

    res = await authenticated_buyer.post(
        "/users/refresh-token",
        json={"refresh_token": refresh_token},
    )


async def test_refresh_token_with_wrong_refresh_token(authenticated_buyer):
    res = await authenticated_buyer.post(
        "/users/refresh-token",
        json={"refresh_token": "wrong_refresh_token"},
    )
    assert res.status_code == 401


async def test_partial_update_user(authenticated_buyer):
    res = await authenticated_buyer.patch(
        "/users",
        json={"first_name": "Jonny"},
    )

    assert res.status_code == 200
    assert res.json()["first_name"] == "Jonny"


async def test_partial_update_user_with_the_same_email(authenticated_buyer):

    with patch("app.domains.users.service.UserService.partial_update_user") as mock_obj:
        mock_obj.side_effect = UserAlreadyExistsException

        res = await authenticated_buyer.patch(
            "/users",
            json={"email": "user@example.com"},
        )

        assert res.status_code == 409
        mock_obj.assert_called_once()


async def test_partial_update_non_existing_user(authenticated_buyer):

    with patch("app.domains.users.service.UserService.partial_update_user") as mock_obj:
        mock_obj.side_effect = UserNotFoundException

        res = await authenticated_buyer.patch(
            "/users",
            json={"last_name": "last_name"},
        )

        assert res.status_code == 404
        mock_obj.assert_called_once()


async def test_delete_user_with_not_enough_permissions(authenticated_buyer):
    res = await authenticated_buyer.delete("/users/1")

    assert res.status_code == 403


async def test_delete_user(admin_user, async_client):
    res = await async_client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {admin_user}"},
    )

    assert res.json() == {"message": "User deleted"}


async def test_delete_non_existing_user(authenticated_admin):
    with patch("app.domains.users.service.UserService.delete_user") as mock_obj:
        mock_obj.side_effect = UserNotFoundException

        res = await authenticated_admin.delete("/users/123")

        assert res.status_code == 404
        mock_obj.assert_called_once_with(123)
