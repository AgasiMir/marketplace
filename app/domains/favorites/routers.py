import asyncio
from fastapi import APIRouter, Depends, status
from app.domains.dependencies import DBDep, UserDep
from app.domains.favorites.schemas import FavoriteCreate, FavoritePublic
from app.exceptions.fastapi_exceptions import (
    FavoriteAlreadyExistsHTTPException,
    FavoriteLimitExceededHTTPException,
    FavoriteNotFoundHTTPException,
    ProductNotFoundHTTPException,
)
from app.exceptions.python_exceptions import (
    FavoriteAlreadyExistsException,
    FavoriteLimitExceededException,
    FavoriteNotFoundException,
    ProductNotFoundException,
)

from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/favorites",
    tags=["favorites 💖💖"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(10, Duration.SECOND * 2))))],
)


@router.get("", summary="Get Favorites", response_model=list[FavoritePublic])
async def get_favorites(db: DBDep, current_user: UserDep):
    await asyncio.sleep(2)
    return await db.favorites.get_favorites(current_user.id)


@router.post("", summary="Add Favorite", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    db: DBDep, current_user: UserDep, create_favorite: FavoriteCreate
):
    try:
        return await db.favorites.add_favorite(current_user.id, create_favorite)
    except FavoriteAlreadyExistsException:
        raise FavoriteAlreadyExistsHTTPException
    except ProductNotFoundException:
        raise ProductNotFoundHTTPException
    except FavoriteLimitExceededException:
        raise FavoriteLimitExceededHTTPException


@router.delete("/{product_id}", summary="Delete Favorite")
async def delete_favorite(db: DBDep, current_user: UserDep, product_id: int):
    try:
        return await db.favorites.delete_favorite(current_user.id, product_id)
    except FavoriteNotFoundException:
        raise FavoriteNotFoundHTTPException
