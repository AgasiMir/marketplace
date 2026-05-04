from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import create_access_token, create_refresh_token, verify_password
from app.exceptions.python_exceptions import (
    IncorrectCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.models.user import User
from app.domains.users.schemas import UserCreate, UserPartialUpdate, UserPublic


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _from_db(self, model) -> UserPublic:
        return UserPublic.model_validate(model)

    async def _check_if_user_exists(self, email: str, username: str) -> bool:

        res = await self.session.scalar(
            select(User).where(
                or_(
                    User.email == email,
                    User.username == username,
                )
            )
        )

        return True if res else False

    async def _get_user_by_username(self, username: str) -> User:

        return await self.session.scalar(
            select(User).where(
                User.username == username,
                User.is_active,
            )
        )

    async def _select_user_for_update(self, user_id: int) -> User:
        return await self.session.scalar(
            select(User)
            .where(
                User.id == user_id,
                User.is_active,
            )
            .with_for_update()
        )

    async def get_user_profile(self, username: str) -> UserPublic:
        user = await self._get_user_by_username(username)
        return self._from_db(user)

    async def create_user(self, create_user: UserCreate) -> UserPublic:
        if await self._check_if_user_exists(create_user.email, create_user.username):
            raise UserAlreadyExistsException

        db_user = User(**create_user.model_dump())

        self.session.add(db_user)
        await self.session.flush()

        return self._from_db(db_user)

    async def login_user(self, username: str, password: str) -> dict:
        user = await self._get_user_by_username(username)

        if not user or not verify_password(password, user.password):
            raise IncorrectCredentialsException

        access_token = create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "role": f"{user.role}",
            }
        )
        refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "id": user.id,
                "role": f"{user.role}",
            }
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_token(self, username: str) -> dict:
        user = await self._get_user_by_username(username)

        access_token = create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "role": f"{user.role}",
            }
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def partial_update_user(
        self, user_id: int, patch_user: UserPartialUpdate
    ) -> UserPublic:

        if patch_user.email or patch_user.username:
            if await self._check_if_user_exists(patch_user.email, patch_user.username):
                raise UserAlreadyExistsException

        db_user = await self._select_user_for_update(user_id)

        if not db_user:
            raise UserNotFoundException

        for key, value in patch_user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)

        return self._from_db(db_user)

    async def delete_user(self, user_id: int) -> dict:
        user = await self._select_user_for_update(user_id)

        if not user:
            raise UserNotFoundException

        user.is_active = False

        return {"message": "User deleted"}
