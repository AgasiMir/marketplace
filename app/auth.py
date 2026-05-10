from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
import jwt

from app.config import settings
from app.middlewares.log import logger


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 3


# Создаём контекст для хеширования с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """
    Создаёт JWT с payload (sub, role, id, exp, iat).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(timezone.utc)
    to_encode |= {
        "exp": expire,
        "iat": iat,
        "token_type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    iat = datetime.now(timezone.utc)
    to_encode |= {
        "exp": expire,
        "iat": iat,
        "token_type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> bool:
    """
    Валидирует JWT access-токен.

    Декодирует токен с использованием секретного ключа и алгоритма из настроек,
    проверяет наличие обязательных полей (sub, token_type) и убеждается,
    что token_type равен "access". Также проверяет срок действия токена.

    Используется в связке с AdminAuth для аутентификации административной панели,
    а также может применяться для быстрой проверки валидности токена без
    обращения к базе данных.

    Args:
        token (str): JWT access-токен в виде строки.

    Returns:
        bool: True если токен валиден (не истёк, корректный тип, содержит sub),
              False в противном случае.

    Raises:
        Не поднимает исключений, все ошибки логируются и возвращаются как False.

    Пример использования в AdminAuth:
        class AdminAuth(AuthenticationBackend):
            async def login(self, request: Request) -> bool:
                ...
                access_token = create_access_token(...)
                if not decode_token(access_token):
                    return False
                ...

            async def authenticate(self, request: Request) -> bool:
                token = request.session.get("access_token")
                if not token or not decode_token(token):
                    return False
                return True
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if email is None or token_type != "access":
            logger.error("Could not validate token")
            return False

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return False

    except jwt.PyJWTError:
        logger.error("Could not validate token")
        return False

    return True
