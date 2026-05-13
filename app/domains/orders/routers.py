from fastapi import APIRouter, Depends, status
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

from app.domains.dependencies import DBDep, UserDep, PaginationDep
from app.domains.orders.schemas import OrderListPublic, OrderPublic
from app.exceptions.fastapi_exceptions import (
    CartIsEmptyHTTPException,
    FailedToLoadOrderHTTPException,
    OrderNotFoundHTTPException,
    ProductIsOutOfStockHTTPException,
    ProductIsUnavailableHTTPException,
    ProductWithNoPriceHTTPException,
)
from app.exceptions.python_exceptions import (
    CartIsEmptyException,
    FailedToLoadOrderException,
    OrderNotFoundException,
    ProductIsOutOfStockException,
    ProductIsUnavailableException,
    ProductWithNoPriceException,
)


router = APIRouter(
    prefix="/orders",
    tags=["orders 📦📦"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(10, Duration.SECOND * 2))))],
)


@router.post(
    "/checkout", status_code=status.HTTP_201_CREATED, response_model=OrderPublic
)
async def checkout_order(db: DBDep, current_user: UserDep):
    """
    Создаёт заказ на основе текущей корзины пользователя.
    Сохраняет позиции заказа, вычитает остатки и очищает корзину.
    """

    try:
        return await db.orders.checkout_order(current_user.id)
    except CartIsEmptyException:
        raise CartIsEmptyHTTPException
    except ProductIsUnavailableException as err:
        raise ProductIsUnavailableHTTPException(err.detail)
    except ProductIsOutOfStockException as err:
        raise ProductIsOutOfStockHTTPException(err.detail)
    except ProductWithNoPriceException as err:
        raise ProductWithNoPriceHTTPException(err.detail)
    except FailedToLoadOrderException:
        raise FailedToLoadOrderHTTPException


@router.get("", summary="Get User's Orders", response_model=OrderListPublic)
async def get_orders(db: DBDep, current_user: UserDep, pagination: PaginationDep):
    return await db.orders.get_orders(
        user_id=current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{order_id}", summary="Get User's Order", response_model=OrderPublic)
async def get_order(order_id: int, db: DBDep, current_user: UserDep):
    try:
        return await db.orders.get_order(
            order_id=order_id,
            user_id=current_user.id,
        )
    except OrderNotFoundException:
        raise OrderNotFoundHTTPException
