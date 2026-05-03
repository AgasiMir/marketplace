import pytest
from app.uow.uow import DBManager
from app.models import Category
from app.domains.categories.schemas import (
    CategoryCreate,
    CategoryPublic,
    CategoryPartialUpdate,
)
from app.exceptions.python_exceptions import CategoryNotFoundException


@pytest.fixture
async def categories():
    cat_1_data = {"name": "Laptops"}
    cat_2_data = {"name": "Smartphones", "parent_id": 2}

    cat_1 = CategoryCreate(**cat_1_data)
    cat_2 = CategoryCreate(**cat_2_data)

    return cat_1, cat_2


async def test_get_categories(db: DBManager, categories):
    cat_1, cat_2 = categories

    db_cat_1 = Category(**cat_1.model_dump())
    db_cat_2 = Category(**cat_2.model_dump())

    db.add(db_cat_1)
    db.add(db_cat_2)

    await db.flush()

    res = await db.categories.get_categories(0, 10, "name")

    assert len(res) == 2
    assert res[0].name == "Laptops"
    assert isinstance(res[1], CategoryPublic)


async def test_create_category(db: DBManager, categories):
    cat_1, _ = categories
    await db.categories.create_category(cat_1)

    res = await db.categories.get_categories(0, 10, "name")

    assert len(res) == 1
    assert isinstance(res[0], CategoryPublic)


async def test_partial_update_category(db: DBManager, categories):
    cat_1, _ = categories
    partial_updata_data = CategoryPartialUpdate(**{"name": "Laptops!!!"})
    db_cat = await db.categories.create_category(cat_1)

    res = await db.categories.partial_update_category(db_cat.id, partial_updata_data)
    assert res.name == "Laptops!!!"


async def test_delete_category(db: DBManager, categories):
    cat_1, _ = categories
    db_cat = await db.categories.create_category(cat_1)

    res = await db.categories.delete_category(db_cat.id)
    assert res == {"message": "Category deleted"}


async def test_partial_update_non_existing_category(db: DBManager):
    partial_updata_data = CategoryPartialUpdate(**{"name": "Laptops!!!"})

    with pytest.raises(CategoryNotFoundException):
        await db.categories.partial_update_category(123, partial_updata_data)


async def test_delete_non_existing_category(db: DBManager):

    with pytest.raises(CategoryNotFoundException):
        await db.categories.delete_category(123)
