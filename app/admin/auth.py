from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.auth import create_access_token, verify_password
from app.models.user import UserRole

from app.domains.users.repository import UserRepository

from app.core.database import async_session
from app.config import settings
from app.auth import decode_token


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        user = await UserRepository(async_session()).get_user_by_username(username)
        if (
            not user
            or not verify_password(password, user.password)
            or not user.is_active
            or user.role != UserRole.admin
        ):
            return False

        access_token = create_access_token(
            data={
                "sub": user.email,
                "id": user.id,
                "role": str(user.role),
            }
        )

        if not decode_token(access_token):
            return False

        request.session.update({"access_token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("access_token")

        if not token:
            return False

        if not decode_token(token):
            return False

        return True


authentication_backend = AdminAuth(
    secret_key=settings.authentication_backend_secret_key
)
