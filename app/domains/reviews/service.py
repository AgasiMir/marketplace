from app.domains.reviews.schemas import ReviewCreate, ReviewPublic
from app.email import send_email_async
from app.uow.uow import DBManager


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
            send_email_async.delay(
                email,
                "Добавление отзыва",
                body=f"{username}. Спасибо за отзыв:\n\nОтзыв: {res.comment}",
            )
            return res

    async def delete_review(self, review_id: int, user_id: int, user_role: str) -> dict:
        return await self.db_manager.reviews.delete_review(
            review_id=review_id,
            user_id=user_id,
            user_role=user_role,
        )
