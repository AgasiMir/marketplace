from app.domains.users.schemas import UserCreate, UserPartialUpdate
from app.auth import verify_password


async def test_user_create_schema():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": "1234abcd",
        "role": "buyer",
    }
    user_create = UserCreate(**data)
    assert user_create.first_name == "John"
    assert verify_password(data["password"], user_create.password)


async def test_user_partial_update_schema_with_new_password():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": "1234abcd",
    }
    user_partial_update = UserPartialUpdate(**data)
    assert user_partial_update.username == "JD"
    assert verify_password(data["password"], user_partial_update.password)


async def test_user_partial_update_schema_without_new_password():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": None,
    }
    user_partial_update = UserPartialUpdate(**data)
    assert user_partial_update.username == "JD"
