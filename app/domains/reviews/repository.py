from asyncpg import NotNullViolationError
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.python_exceptions import (
    OnlyAuthorOrAdminCanDeleteReviewException,
    ProductNotFoundException,
    ReviewNotFoundException,
)
from app.models import Product, Review, User, Category

from app.domains.reviews.schemas import ReviewCreate, ReviewPublic


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _check_if_product_exists(self, product_id: int) -> Product:
        return await self.session.scalar(
            select(Product)
            .join(Product.category)
            .join(Product.seller)
            .where(
                Product.id == product_id,
                Product.is_active,
                Category.is_active,
                User.is_active,
            )
        )

    async def _check_if_review_exists(self, user_id: int, product_id: int) -> Review:
        return await self.session.scalar(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == product_id,
            )
        )

    async def _set_product_rating(self, product_id: int):
        product = await self._check_if_product_exists(product_id)

        stmt = text("""SELECT AVG(grade) 
                        FROM reviews
                        WHERE product_id = :product_id
                        AND reviews.is_active = True""").params(product_id=product_id)

        avg_rating = await self.session.scalar(stmt) or 0.0
        product.rating = round(avg_rating, 2)
        await self.session.flush()

    async def create_review(
        self,
        user_id: int,
        create_review: ReviewCreate,
    ) -> ReviewPublic:

        if not await self._check_if_product_exists(create_review.product_id):
            raise ProductNotFoundException

        review = await self._check_if_review_exists(user_id, create_review.product_id)

        if review:
            review.is_active = True
            for key, value in create_review.model_dump(exclude_unset=True).items():
                setattr(review, key, value)

        else:
            if not create_review.grade:
                raise NotNullViolationError

            review = Review(**create_review.model_dump(), user_id=user_id)

            self.session.add(review)
            await self.session.flush()

        await self._set_product_rating(create_review.product_id)
        return ReviewPublic.model_validate(review)

    async def delete_review(self, review_id: int, user_id: int, user_role: str) -> dict:
        review = await self.session.scalar(
            select(Review).where(
                Review.id == review_id,
                Review.is_active,
            )
        )
        if not review:
            raise ReviewNotFoundException

        if review.user_id != user_id and user_role != "admin":
            raise OnlyAuthorOrAdminCanDeleteReviewException

        review.is_active = False

        await self._set_product_rating(review.product_id)
        return {"message": "Review Deleted"}
