from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.auth import create_access_token, verify_password
from app.models.user import UserRole

from app.domains.users.repository import UserRepository

from app.core.database import async_session
from app.config import settings
from app.auth import decode_token


class AdminAuth(AuthenticationBackend):
    """
    Бэкенд аутентификации для административной панели SQLAdmin.

    Обеспечивает вход, выход и проверку аутентификации администраторов
    через сессионные JWT-токены. Требует, чтобы пользователь имел роль
    администратора (UserRole.admin) и был активен.

    Attributes:
        secret_key (str): Секретный ключ для подписи токенов, передаётся
            в конструктор из настроек.
    """

    async def login(self, request: Request) -> bool:
        """
        Обрабатывает вход администратора.

        Извлекает username и password из формы запроса, проверяет
        существование пользователя, корректность пароля, активность
        и роль администратора. При успехе генерирует JWT-токен,
        сохраняет его в сессии и возвращает True.

        Args:
            request (Request): Объект запроса Starlette, содержащий форму.

        Returns:
            bool: True если аутентификация успешна, иначе False.
        """

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
        """
        Обрабатывает выход администратора.

        Очищает все данные сессии, удаляя JWT-токен аутентификации.

        Args:
            request (Request): Объект запроса Starlette.

        Returns:
            bool: Всегда возвращает True.
        """

        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Проверяет аутентификацию администратора на основе сессии.

        Извлекает JWT-токен из сессии и проверяет его валидность
        с помощью decode_token.

        Args:
            request (Request): Объект запроса Starlette.

        Returns:
            bool: True если токен присутствует и валиден, иначе False.
        """

        token = request.session.get("access_token")

        if not token:
            return False

        if not decode_token(token):
            return False

        return True


authentication_backend = AdminAuth(
    secret_key=settings.authentication_backend_secret_key
)
