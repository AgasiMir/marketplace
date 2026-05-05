import pytest
from app.exceptions.python_exceptions import WrongSortByException
from app.uow.uow import DBManager
from app.domains.categories.schemas import CategoryCreate, CategoryPartialUpdate
from app.domains.categories.service import CategoryService
from app.utils.utils import Pagination


@pytest.fixture
async def categories():
    cat_1_data = {"name": "Laptops"}
    cat_2_data = {"name": "Smartphones", "parent_id": 2}

    cat_1 = CategoryCreate(**cat_1_data)
    cat_2 = CategoryCreate(**cat_2_data)

    return cat_1, cat_2


async def test_get_categories(db: DBManager, categories):
    cat_1, cat_2 = categories

    await CategoryService(db).create_category(cat_1)
    await CategoryService(db).create_category(cat_2)

    pagination = Pagination(page=1, page_size=10)

    res = await CategoryService(db).get_categories(pagination, "id", "desc")
    assert len(res) == 2


async def test_create_category(db: DBManager, categories):
    cat_1, _ = categories
    db_category = await CategoryService(db).create_category(cat_1)

    assert db_category.name == "Laptops"


async def test_partial_update_category(db: DBManager, categories):
    cat_1, _ = categories
    partial_update_data = CategoryPartialUpdate(**{"name": "Laptops!!!"})
    db_category = await CategoryService(db).create_category(cat_1)

    res = await CategoryService(db).partial_update_category(
        db_category.id, partial_update_data
    )
    assert res.name == "Laptops!!!"


async def test_delete_category(db: DBManager, categories):
    cat_1, _ = categories
    db_category = await CategoryService(db).create_category(cat_1)

    res = await CategoryService(db).delete_category(db_category.id)
    assert res["message"] == "Category deleted"


async def test_get_categories_with_wrong_sort_by(db: DBManager, categories):
    cat_1, cat_2 = categories

    await CategoryService(db).create_category(cat_1)
    await CategoryService(db).create_category(cat_2)

    pagination = Pagination(page=1, page_size=10)

    with pytest.raises(WrongSortByException):
        await CategoryService(db).get_categories(pagination, "created_at", "desc")
