from app.domains.reviews.schemas import ReviewCreate, ReviewPublic
from app.email import send_email_async
from app.uow.uow import DBManager
from app.init import redis_manager
from app.middlewares.log import logger


class ReviewService:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    async def create_review(
        self,
        user_id: int,
        create_review: ReviewCreate,
        email: str,
        username: str,
    ) -> ReviewPublic:
        res = await self.db_manager.reviews.create_review(
            user_id=user_id,
            create_review=create_review,
        )

        if res:
            pattern = f"fastapi-cache:product:{create_review.product_id}:user:*"
            deleted_count = await redis_manager.delete_by_pattern(pattern)
            logger.info(
                f"Удалено ключей кэша для продукта {create_review.product_id}: {deleted_count}"
            )

            send_email_async.delay(
                email,
                "Добавление отзыва",
                body=f"{username}. Спасибо за отзыв:\n\nОтзыв: {res.comment}",
            )

            return res

    async def delete_review(self, review_id: int, user_id: int, user_role: str) -> dict:
        res = await self.db_manager.reviews.delete_review(
            review_id=review_id,
            user_id=user_id,
            user_role=user_role,
        )

        if res:
            pattern = f"fastapi-cache:product:{res['product_id']}:user:*"
            deleted_count = await redis_manager.delete_by_pattern(pattern)
            logger.info(
                f"Удалено ключей кэша для продукта {res['product_id']}: {deleted_count}"
            )

            return res
