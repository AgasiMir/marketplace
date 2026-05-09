from app.domains.reviews.service import ReviewService
from app.domains.reviews.schemas import ReviewCreate
from app.uow.uow import DBManager


async def test_create_review_service(category_user_product, db: DBManager):
    review = ReviewCreate(**{"product_id": 1, "comment": "test", "grade": 4})
    res = await ReviewService(db).create_review(
        user_id=1,
        create_review=review,
        email="user@example.com",
        username="username",
    )
    assert res.comment == review.comment


async def test_delete_review_service(category_user_product, db: DBManager):
    review = ReviewCreate(**{"product_id": 1, "comment": "test", "grade": 4})
    res = await ReviewService(db).create_review(
        user_id=1,
        create_review=review,
        email="user@example.com",
        username="username",
    )

    assert res.comment == review.comment

    res = await ReviewService(db).delete_review(res.id, res.user_id, "seller")
    assert res["message"] == "Review Deleted"
