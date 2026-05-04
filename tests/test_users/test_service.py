import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.schemas import UserCreate, UserPublic, UserPartialUpdate
from app.domains.users.service import UserService
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


async def test_get_user_profile(test_user, db: DBManager):
    res = await UserService(db).get_user_profile(test_user.username)
    assert isinstance(res, UserPublic)


async def test_create_user(db: DBManager):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD",
        "email": "user@example.com",
        "password": "1234abcd",
        "role": "buyer",
    }
    res = await UserService(db).create_user(UserCreate(**data))
    assert res.id is not None
    assert isinstance(res, UserPublic)


async def test_login(test_user, db: DBManager):
    res = await UserService(db).login(test_user.username, "1234abcd")
    assert res.get("access_token") is not None


async def test_partial_update_user(test_user, db: DBManager):
    data = {"first_name": "John"}
    res = await UserService(db).partial_update_user(
        test_user.id,
        UserPartialUpdate(**data),
    )
    assert isinstance(res, UserPublic)


async def test_delete_user(test_user, db: DBManager):
    await UserService(db).delete_user(test_user.id)


async def test_refresh_token(test_user, db: DBManager):
    res = await UserService(db).login(test_user.username, "1234abcd")
    refresh_token = res.get("refresh_token")

    await UserService(db).refresh_token(refresh_token)
