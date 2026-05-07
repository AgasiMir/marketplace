from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from app.domains.users.schemas import UserCreate, UserPublic, UserPartialUpdate
from app.email import send_email_async
from app.exceptions.python_exceptions import CredentialsException, UserNotFoundException
from app.uow.uow import DBManager


class UserService:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    async def get_user_profile(self, username: str) -> UserPublic:
        return await self.db_manager.users.get_user_profile(username)

    async def create_user(self, create_user: UserCreate) -> UserPublic:
        res = await self.db_manager.users.create_user(create_user)

        if res:
            send_email_async.delay(
                create_user.email,
                "Регистрация на сайте",
                body=f"{create_user.username}!\n\nДобро пожаловать",
            )
            return res

    async def login(self, username: str, password: str, client_host: str) -> dict:
        res = await self.db_manager.users.login_user(username, password)

        if res:
            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            current_datetime = datetime.now(tzinfo)
            current_datetime = datetime.strftime(current_datetime, "%Y-%m-%d %H:%M:%S")

            user = await self.db_manager.users.get_user_profile(username)

            send_email_async.delay(
                user.email,
                "Вход в систему",
                body=f"{user.username}. Был осуществлен вход в систему c IP {client_host}\n\nВремя входа: {current_datetime}",
            )
            return res

    async def refresh_token(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            if username is None or token_type != "refresh":
                raise CredentialsException

        except jwt.ExpiredSignatureError:
            raise CredentialsException
        except jwt.PyJWTError:
            raise CredentialsException

        if not await self.db_manager.users.get_user_by_username(username):
            raise UserNotFoundException

        return await self.db_manager.users.refresh_token(username)

    async def partial_update_user(
        self, user_id: int, patch_user: UserPartialUpdate
    ) -> UserPublic:
        return await self.db_manager.users.partial_update_user(user_id, patch_user)

    async def delete_user(self, user_id: int) -> dict:
        return await self.db_manager.users.delete_user(user_id)
