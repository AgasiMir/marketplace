from pydantic import ValidationError
import pytest
from pytest import raises
from contextlib import nullcontext as does_not_raise
from app.domains.users.schemas import UserCreate, UserPartialUpdate


# fmt: off
@pytest.mark.parametrize(
    "first_name, last_name, username, email, password, role, exc",
    [
        ("John", "Doe", "JD", "user@example.com", "1234abcd", "buyer", does_not_raise()),
        ("John", "Doe", "JD", "user@example.com", "1234abcd", "seller", does_not_raise()),
        ("John", "D", "JD", "user@example.com", "1234abcd", "seller", does_not_raise()),
        ("J", "Doe", "JD", "user@example.com", "1234abcd", "seller", raises(ValidationError)),
        ("  ", "Doe", "JD", "user@example.com", "1234abcd", "seller", raises(ValueError)),
        ("John", "  " * 3, "JD", "user@example.com", "1234abcd", "seller", raises(ValueError)),
        ("John", "Doe", "D", "user@example.com", "1234abcd", "seller", raises(ValidationError)),
        ("John", "Doe", "  ", "user@example.com", "1234abcd", "seller", raises(ValueError)),
        ("John", "Doe", "JD", "user@example", "1234abcd", "seller", raises(ValidationError)),
        ("John", "Doe", "JD", "userexample.com", "1234abcd", "seller", raises(ValidationError)),
        ("John", "Doe", "JD", "user@example.com", "1234ab", "seller", raises(ValidationError)),
        ("John", "Doe", "JD", "user@example.com", "  " * 20, "seller", raises(ValueError)),
        ("John", "Doe", "JD", "user@example.com", "1234ab" * 200, "seller", raises(ValidationError)),
        ("John", "Doe", "JD", "user@example.com", "1234abcd", "admin", raises(ValidationError)),
    ],
)
async def test_user_create_schema(first_name, last_name, username, email, password, role, exc):
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "email": email,
        "password": password,
        "role": role,
    }
    with exc:
        UserCreate(**data)

# fmt: on
@pytest.mark.parametrize(
    "first_name, last_name, username, email, password, exc",
    [
        ("John", "Doe", "JD", "user@example.com", "1234abcd", does_not_raise()),
        ("John", None, None, "user@example.net", None, does_not_raise()),
        ("John", "D", "JD", "user@example.com", "1234abcd", does_not_raise()),
        ("J", "Doe", "JD", "user@example.com", "1234abcd", raises(ValidationError)),
        ("  ", "Doe", "JD", "user@example.com", "1234abcd", raises(ValueError)),
        ("John", "  " * 3, "JD", "user@example.com", "1234abcd", raises(ValueError)),
        ("John", "Doe", "D", "user@example.com", "1234abcd", raises(ValidationError)),
        ("John", "Doe", "  ", "user@example.com", "1234abcd", raises(ValueError)),
        ("John", "Doe", "JD", "user@example", "1234abcd", raises(ValidationError)),
        ("John", "Doe", "JD", "userexample.com", "1234abcd", raises(ValidationError)),
        ("John", "Doe", "JD", "user@example.com", "1234ab", raises(ValidationError)),
        ("John", "Doe", "JD", "user@example.com", "  " * 20, raises(ValueError)),
        (
            "John",
            "Doe",
            "JD",
            "user@example.com",
            "1234ab" * 200,
            raises(ValidationError),
        ),
    ],
)
async def test_user_partial_update_schema(
    first_name, last_name, username, email, password, exc
):
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "email": email,
        "password": password,
    }
    with exc:
        UserPartialUpdate(**data)
