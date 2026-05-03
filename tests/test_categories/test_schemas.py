import pytest
from pydantic import ValidationError
from contextlib import nullcontext as does_not_raise
from app.domains.categories.schemas import CategoryCreate


@pytest.mark.parametrize(
    "name, parent_id, exc",
    [
        ("Smartphones", 1, does_not_raise()),
        ("Laptops", "2", does_not_raise()),
        ("Laptops", None, does_not_raise()),
        ("Laptops", "abc", pytest.raises(ValidationError)),
        ("La", 3, pytest.raises(ValidationError)),
        ("La" * 30, 3, pytest.raises(ValidationError)),
    ],
)
async def test_create_category(name, parent_id, exc):
    data = {"name": name, "parent_id": parent_id}
    with exc:
        CategoryCreate(**data)
