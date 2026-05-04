import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.schemas import UserCreate, UserPublic, UserPartialUpdate
from app.exceptions.python_exceptions import (
    IncorrectCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.models import User
from app.uow.uow import DBManager


@pytest.fixture
async def test_user(db: AsyncSession):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": "1234abcd",
        "role": "buyer",
    }

    user = UserCreate(**data)

    db_user = User(**user.model_dump())

    db.add(db_user)
    await db.flush()

    return db_user


async def test_get_user_profile(test_user: User, db: DBManager):
    res = await db.users.get_user_profile(test_user.username)
    assert res.username == "JD"
    assert isinstance(res, UserPublic)


async def test_create_user(db: DBManager):
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "username": "J_Doe",
        "email": "user@example.org",
        "password": "1234abcd",
        "role": "seller",
    }

    res = await db.users.create_user(UserCreate(**data))

    assert res.id is not None


async def test_create_user_with_existing_email(test_user, db: DBManager):
    data = {
        "first_name": "Peter",
        "last_name": "Parker",
        "username": "Spider Man",
        "email": "user@example.com",
        "password": "1234abcd",
        "role": "buyer",
    }

    with pytest.raises(UserAlreadyExistsException):
        await db.users.create_user(UserCreate(**data))


async def test_create_already_existing_user(test_user, db: DBManager):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": "1234abcd",
        "role": "buyer",
    }

    with pytest.raises(UserAlreadyExistsException):
        await db.users.create_user(UserCreate(**data))


async def test_partial_update_user(test_user, db: DBManager):
    data = {"first_name": "Jonny"}
    res = await db.users.partial_update_user(test_user.id, UserPartialUpdate(**data))
    assert res.first_name == "Jonny"


async def test_partial_update_user_with_existing_username(test_user, db: DBManager):
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "username": "J_Doe",
        "email": "user@example.org",
        "password": "1234abcd",
        "role": "seller",
    }

    update_data = {"username": "JD"}

    res = await db.users.create_user(UserCreate(**data))

    with pytest.raises(UserAlreadyExistsException):
        await db.users.partial_update_user(res.id, UserPartialUpdate(**update_data))


async def test_partial_update_non_existing_user(db: DBManager):
    with pytest.raises(UserNotFoundException):
        await db.users.partial_update_user(
            123,
            UserPartialUpdate(**{"first_name": "Jonny"}),
        )


async def test_delete_user(test_user, db: DBManager):
    res = await db.users.delete_user(test_user.id)
    assert res["message"] == "User deleted"


async def test_delete_non_existing_user(db: DBManager):
    with pytest.raises(UserNotFoundException):
        await db.users.delete_user(123)


async def test_login_user(test_user, db: DBManager):
    res = await db.users.login_user(test_user.username, "1234abcd")
    assert isinstance(res, dict)


async def test_login_user_with_wrong_password(test_user, db: DBManager):
    with pytest.raises(IncorrectCredentialsException):
        await db.users.login_user(test_user.username, "1234abcd___")


async def test_refresh_token(test_user, db: DBManager):
    res = await db.users.refresh_token(test_user.username)
    assert res["token_type"] == "bearer"
