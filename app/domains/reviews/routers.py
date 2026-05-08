from asyncpg import NotNullViolationError
from fastapi import APIRouter, Body, HTTPException, status

from app.domains.dependencies import ReviewServiceDep, UserDep
from app.domains.reviews.schemas import ReviewCreate, ReviewPublic
from app.exceptions.fastapi_exceptions import (
    OnlyAuthorOrAdminCanDeleteReviewHTTPException,
    ProductNotFoundHTTPException,
    ReviewNotFoundHTTPException,
)
from app.exceptions.python_exceptions import (
    OnlyAuthorOrAdminCanDeleteReviewException,
    ProductNotFoundException,
    ReviewNotFoundException,
)


router = APIRouter(prefix="/reviews", tags=["reviews 😀😡"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReviewPublic)
async def create_review(
    reviews: ReviewServiceDep,
    current_user: UserDep,
    create_review: ReviewCreate = Body(
        openapi_examples={
            "1": {
                "summary": "4th Grade Review",
                "value": {"product_id": 1, "comment": "Nice", "grade": 4},
            }
        }
    ),
):
    try:
        return await reviews.create_review(
            user_id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            create_review=create_review,
        )
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    except NotNullViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пожалуйста, выставите оценку",
        )


@router.delete("/{review_id}")
async def delete_review(
    review_id: int, reviews: ReviewServiceDep, current_user: UserDep
) -> dict:
    try:
        return await reviews.delete_review(
            review_id=review_id,
            user_id=current_user.id,
            user_role=current_user.role,
        )
    except ReviewNotFoundException:
        raise ReviewNotFoundHTTPException
    except OnlyAuthorOrAdminCanDeleteReviewException:
        raise OnlyAuthorOrAdminCanDeleteReviewHTTPException
