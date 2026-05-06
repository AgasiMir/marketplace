from typing import Annotated
from fastapi import Depends

import jwt
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

from app.core.database import async_session
from app.exceptions.fastapi_exceptions import (
    AdminOnlyHTTPException,
    CredentialsHTTPException,
    JWTExpiredSignatureException,
    SellerOnlyHTTPException,
)
from app.models.user import User, UserRole
from app.uow.uow import DBManager

from app.utils.utils import Pagination

from app.domains.categories.service import CategoryService
from app.domains.users.service import UserService
from app.domains.products.service import ProductService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)

# Зависимость для пагинации
PaginationDep = Annotated[Pagination, Depends()]


# Зависимость для получения базы данных
# ---------------------------------------------------------------
async def get_db():
    async with DBManager(session_factory=async_session) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
# ---------------------------------------------------------------


# Зависимость для получения текущего пользователя
# ---------------------------------------------------------------
async def get_current_user(db: DBDep, token: str = Depends(oauth2_scheme)):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if username is None or token_type != "access":
            raise CredentialsHTTPException
    except jwt.ExpiredSignatureError:
        raise JWTExpiredSignatureException

    except jwt.PyJWTError:
        raise CredentialsHTTPException

    user = await db.users.get_user_by_username(username)

    if user is None:
        raise CredentialsHTTPException
    return user


UserDep = Annotated[User, Depends(get_current_user)]
# ---------------------------------------------------------------


# Зависимость для получения текущего пользователя (опционально)
# ---------------------------------------------------------------
async def get_optional_current_user(
    db: DBDep, token: str | None = Depends(oauth2_scheme)
) -> User | None:
    """
    Аналогичен get_current_user, но возвращает None для неаутентифицированных.
    """
    if token is None:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if username is None or token_type != "access":
            return None
    except (jwt.ExpiredSignatureError, jwt.PyJWTError):
        return None

    user = await db.users.get_user_by_username(username)
    return user  # может быть None, если пользователь не найден


OptionalUserDep = Annotated[User | None, Depends(get_optional_current_user)]
# ---------------------------------------------------------------


# Зависимость для получения продавца
# ---------------------------------------------------------------
async def get_seller(user: UserDep):
    if user.role != UserRole.seller:
        raise SellerOnlyHTTPException
    return user


SellerDep = Annotated[User, Depends(get_seller)]
# ---------------------------------------------------------------


# Зависимость для получения администратора
# ---------------------------------------------------------------
async def get_admin(user: UserDep):
    if user.role != UserRole.admin:
        raise AdminOnlyHTTPException
    return user


AdminDep = Annotated[User, Depends(get_admin)]
# ---------------------------------------------------------------


# Зависимость для получения сервиса категорий
# ---------------------------------------------------------------
async def get_category_service(db_manager: DBDep) -> CategoryService:
    return CategoryService(db_manager=db_manager)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
# ---------------------------------------------------------------


# Зависимость для получения сервиса пользователей
# ---------------------------------------------------------------
async def get_user_service(db_manager: DBDep) -> UserService:
    return UserService(db_manager=db_manager)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
# ---------------------------------------------------------------


# Зависимость для получения сервиса продуктов
# ---------------------------------------------------------------
async def get_product_service(db_manager: DBDep) -> ProductService:
    return ProductService(db_manager=db_manager)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
# ---------------------------------------------------------------
