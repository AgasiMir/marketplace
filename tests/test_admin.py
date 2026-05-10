"""
Тесты для админ-панели (AdminAuth).

Проверяет аутентификацию и авторизацию административной панели,
реализованную в классе AdminAuth (app/admin/auth.py).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.requests import Request
from starlette.datastructures import FormData

from app.admin.auth import AdminAuth
from app.models.user import UserRole
from app.auth import hash_password


@pytest.fixture
def admin_auth():
    """Фикстура для экземпляра AdminAuth."""
    return AdminAuth(secret_key="test-secret-key")


@pytest.fixture
def mock_request():
    """Создаёт mock-объект Request с необходимыми атрибутами."""
    request = MagicMock(spec=Request)
    request.session = {}
    return request


@pytest.fixture
def admin_user_data():
    """Данные пользователя с ролью admin."""
    return {
        "email": "admin@example.com",
        "password": hash_password("correctpassword"),
        "role": UserRole.admin,
        "is_active": True,
        "id": 1,
    }


@pytest.fixture
def regular_user_data():
    """Данные пользователя с ролью user (не admin)."""
    return {
        "email": "user@example.com",
        "password": hash_password("correctpassword"),
        "role": UserRole.buyer,
        "is_active": True,
        "id": 2,
    }


class TestAdminAuthLogin:
    """Тесты для метода login класса AdminAuth."""

    @pytest.mark.asyncio
    async def test_login_success(self, admin_auth, mock_request, admin_user_data):
        """Успешный логин с правильными credentials и ролью admin."""
        # Мокаем request.form()
        mock_request.form = AsyncMock(
            return_value=FormData(
                [
                    ("username", admin_user_data["email"]),
                    ("password", "correctpassword"),
                ]
            )
        )

        # Мокаем UserRepository.get_user_by_username
        with patch("app.admin.auth.UserRepository") as MockUserRepo:
            mock_repo = AsyncMock()
            mock_repo.get_user_by_username.return_value = type(
                "User", (), admin_user_data
            )()
            MockUserRepo.return_value = mock_repo

            # Вызываем login
            result = await admin_auth.login(mock_request)

            # Проверяем, что логин успешен
            assert result is True
            # Проверяем, что токен добавлен в сессию
            assert "access_token" in mock_request.session
            token = mock_request.session["access_token"]
            assert isinstance(token, str)
            assert len(token) > 0

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, admin_auth, mock_request, admin_user_data
    ):
        """Логин с неправильным паролем должен вернуть False."""
        mock_request.form = AsyncMock(
            return_value=FormData(
                [("username", admin_user_data["email"]), ("password", "wrongpassword")]
            )
        )

        with patch("app.admin.auth.UserRepository") as MockUserRepo:
            mock_repo = AsyncMock()
            mock_repo.get_user_by_username.return_value = type(
                "User", (), admin_user_data
            )()
            MockUserRepo.return_value = mock_repo

            result = await admin_auth.login(mock_request)
            assert result is False
            # Токен не должен быть добавлен в сессию
            assert "access_token" not in mock_request.session

    @pytest.mark.asyncio
    async def test_login_user_not_admin(
        self, admin_auth, mock_request, regular_user_data
    ):
        """Логин пользователя с ролью user (не admin) должен вернуть False."""
        mock_request.form = AsyncMock(
            return_value=FormData(
                [
                    ("username", regular_user_data["email"]),
                    ("password", "correctpassword"),
                ]
            )
        )

        with patch("app.admin.auth.UserRepository") as MockUserRepo:
            mock_repo = AsyncMock()
            mock_repo.get_user_by_username.return_value = type(
                "User", (), regular_user_data
            )()
            MockUserRepo.return_value = mock_repo

            result = await admin_auth.login(mock_request)
            assert result is False
            assert "access_token" not in mock_request.session

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, admin_auth, mock_request):
        """Логин с несуществующим email должен вернуть False."""
        mock_request.form = AsyncMock(
            return_value=FormData(
                [("username", "nonexistent@example.com"), ("password", "anypassword")]
            )
        )

        with patch("app.admin.auth.UserRepository") as MockUserRepo:
            mock_repo = AsyncMock()
            mock_repo.get_user_by_username.return_value = None
            MockUserRepo.return_value = mock_repo

            result = await admin_auth.login(mock_request)
            assert result is False
            assert "access_token" not in mock_request.session

    @pytest.mark.asyncio
    async def test_login_user_inactive(self, admin_auth, mock_request, admin_user_data):
        """Логин неактивного пользователя должен вернуть False."""
        admin_user_data["is_active"] = False
        mock_request.form = AsyncMock(
            return_value=FormData(
                [
                    ("username", admin_user_data["email"]),
                    ("password", "correctpassword"),
                ]
            )
        )

        with patch("app.admin.auth.UserRepository") as MockUserRepo:
            mock_repo = AsyncMock()
            mock_repo.get_user_by_username.return_value = type(
                "User", (), admin_user_data
            )()
            MockUserRepo.return_value = mock_repo

            result = await admin_auth.login(mock_request)
            assert result is False
            assert "access_token" not in mock_request.session


class TestAdminAuthAuthenticate:
    """Тесты для метода authenticate класса AdminAuth."""

    @pytest.mark.asyncio
    async def test_authenticate_success(self, admin_auth, mock_request):
        """Authenticate с валидным токеном в сессии должен вернуть True."""
        # Создаём валидный токен (мок)
        valid_token = "valid.jwt.token"
        mock_request.session = {"access_token": valid_token}

        # Мокаем decode_token, чтобы она возвращала True
        with patch("app.admin.auth.decode_token") as mock_decode:
            mock_decode.return_value = True

            result = await admin_auth.authenticate(mock_request)
            assert result is True
            mock_decode.assert_called_once_with(valid_token)

    @pytest.mark.asyncio
    async def test_authenticate_no_token(self, admin_auth, mock_request):
        """Authenticate без токена в сессии должен вернуть False."""
        mock_request.session = {}
        result = await admin_auth.authenticate(mock_request)
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, admin_auth, mock_request):
        """Authenticate с невалидным токеном должен вернуть False."""
        invalid_token = "invalid.jwt.token"
        mock_request.session = {"access_token": invalid_token}

        with patch("app.admin.auth.decode_token") as mock_decode:
            mock_decode.return_value = False

            result = await admin_auth.authenticate(mock_request)
            assert result is False
            mock_decode.assert_called_once_with(invalid_token)


class TestAdminAuthLogout:
    """Тесты для метода logout класса AdminAuth."""

    @pytest.mark.asyncio
    async def test_logout_success(self, admin_auth, mock_request):
        """Logout должен очистить сессию и вернуть True."""
        mock_request.session = {"access_token": "some.token", "other": "data"}
        result = await admin_auth.logout(mock_request)
        assert result is True
        assert mock_request.session == {}

    @pytest.mark.asyncio
    async def test_logout_empty_session(self, admin_auth, mock_request):
        """Logout с пустой сессией должен вернуть True."""
        mock_request.session = {}
        result = await admin_auth.logout(mock_request)
        assert result is True
        assert mock_request.session == {}
