from fastapi import APIRouter, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.domains.users.schemas import (
    RefreshTokenRequest,
    UserCreate,
    UserPartialUpdate,
    UserPublic,
)
from app.domains.dependencies import UserServiceDep, UserDep, AdminDep
from app.exceptions.python_exceptions import (
    CredentialsException,
    IncorrectCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.exceptions.fastapi_exceptions import (
    CredentialsHTTPException,
    IncorrectCredentialsHTTPException,
    UserAlreadyExistsHTTPException,
    UserNotFoundHTTPException,
)

from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.SECOND * 2))))],
)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Получить текущего пользователя",
    response_model=UserPublic,
)
async def get_user_profile(users: UserServiceDep, current_user: UserDep):
    return await users.get_user_profile(current_user.username)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Эндпойнт для создания пользователя",
    response_model=UserPublic,
)
async def create_user(
    users: UserServiceDep,
    create_user: UserCreate = Body(
        openapi_examples={
            "1": {
                "summary": "John Doe",
                "value": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "JD",
                    "email": "user@example.com",
                    "password": "1234abcd",
                    "role": "buyer",
                },
            }
        }
    ),
):
    try:
        return await users.create_user(create_user)
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Эндпойнт для входа в систему",
)
async def login(
    users: UserServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    try:
        return await users.login(
            form_data.username,
            form_data.password,
        )
    except IncorrectCredentialsException:
        raise IncorrectCredentialsHTTPException


@router.post(
    "/refresh-token",
    summary="Refresh token",
    description="Эндпойнт для обновления токена",
)
async def refresh_token(users: UserServiceDep, refresh_token: RefreshTokenRequest):
    try:
        return await users.refresh_token(refresh_token.refresh_token)
    except CredentialsException:
        raise CredentialsHTTPException


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Обновление пользователя",
)
async def partial_update_user(
    users: UserServiceDep,
    patch_user: UserPartialUpdate,
    current_user: UserDep,
):
    try:
        return await users.partial_update_user(current_user.id, patch_user)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Эндпойнт для удаления пользователя. Доступен только администратору",
)
async def delete_user(users: UserServiceDep, admin: AdminDep, user_id: int):
    try:
        return await users.delete_user(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
