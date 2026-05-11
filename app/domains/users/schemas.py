from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from enum import StrEnum, auto
from app.auth import hash_password


class UserRoleCreate(StrEnum):
    """
    Перечисление ролей пользователя при создании.

    Возможные значения:
        buyer - покупатель
        seller - продавец
    """

    buyer = auto()
    seller = auto()


class UserPublic(BaseModel):
    """
    Модель для ответа с данными пользователя.
    Используется в User GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор пользователя")
    first_name: str = Field(description="Имя пользователя")
    last_name: str = Field(description="Фамилия пользователя")
    username: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Email пользователя")
    role: str = Field(description="Роль пользователя")
    is_active: bool = Field(description="Активен ли пользователь")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для создания нового пользователя.

    Атрибуты:
        first_name (str): Имя пользователя (2-150 символов)
        last_name (str): Фамилия пользователя (1-150 символов)
        username (str): Ник пользователя (2-50 символов)
        email (EmailStr): Email пользователя (до 150 символов)
        password (str): Пароль (8-255 символов, хешируется автоматически)
        role (UserRoleCreate): Роль пользователя (по умолчанию buyer)

    Валидаторы:
        - Проверяют, что поля не пустые после обрезки пробелов
        - Пароль хешируется с помощью hash_password
    """

    first_name: str = Field(
        min_length=2,
        max_length=150,
        description="Имя пользователя",
    )
    last_name: str = Field(
        min_length=1,
        max_length=150,
        description="Фамилия пользователя",
    )
    username: str = Field(min_length=2, max_length=50, description="Ник пользователя")
    email: EmailStr = Field(max_length=150, description="Email пользователя")
    password: str = Field(
        min_length=8,
        max_length=255,
        description="Пароль (минимум 8 символов, максимум - 255)",
    )
    role: UserRoleCreate = Field(
        default=UserRoleCreate.buyer,
        description="Роль пользователя",
    )

    @field_validator("first_name")
    def check_if_first_name_is_empty(cls, value: str) -> str:
        value = value.strip()

        if len(value) == 0:
            raise ValueError("Имя не может быть пустым")

        return value

    @field_validator("last_name")
    def check_if_last_name_is_empty(cls, value: str) -> str:
        value = value.strip()

        if len(value) == 0:
            raise ValueError("Фамилия не может быть пустой")

        return value

    @field_validator("username")
    def check_if_username_is_empty(cls, value: str) -> str:
        value = value.strip()

        if len(value) == 0:
            raise ValueError("Username не может быть пустым")

        return value

    @field_validator("password", mode="after")
    def hash_password(cls, value: str) -> str:
        """Хеширует пароль перед сохранением"""

        value = value.strip()

        if len(value) == 0:
            raise ValueError("Пароль не может быть пустым")

        return hash_password(value)


class UserPartialUpdate(BaseModel):
    """
    Модель для частичного обновления данных пользователя.

    Все поля опциональны (могут быть None). Если передано значение,
    применяются те же валидации, что и в UserCreate.

    Атрибуты:
        first_name (str | None): Имя пользователя (2-150 символов)
        last_name (str | None): Фамилия пользователя (1-150 символов)
        username (str | None): Ник пользователя (2-50 символов)
        email (EmailStr | None): Email пользователя (до 150 символов)
        password (str | None): Пароль (8-255 символов, хешируется если передан)

    Валидаторы:
        - Проверяют непустоту переданных значений
        - Пароль хешируется только если передан
    """

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Имя пользователя",
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
        description="Фамилия пользователя",
    )
    username: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Ник пользователя",
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=150,
        description="Email пользователя",
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
        description="Пароль (минимум 8 символов, максимум - 255)",
    )

    @field_validator("first_name")
    def check_if_first_name_is_empty(cls, value: str) -> str:
        if value:
            value = value.strip()

            if len(value) == 0:
                raise ValueError("Имя не может быть пустым")
        return value

    @field_validator("last_name")
    def check_if_last_name_is_empty(cls, value: str) -> str:
        if value:
            value = value.strip()

            if len(value) == 0:
                raise ValueError("Фамилия не может быть пустой")
        return value

    @field_validator("username")
    def check_if_username_is_empty(cls, value: str) -> str:

        if value:
            value = value.strip()

            if len(value) == 0:
                raise ValueError("Username не может быть пустым")
        return value

    @field_validator("password", mode="after")
    def hash_password(cls, value: str) -> str:
        """Хеширует пароль перед сохранением"""

        if value:
            value = value.strip()

            if len(value) == 0:
                raise ValueError("Пароль не может быть пустым")

            return hash_password(value)
        return value


class RefreshTokenRequest(BaseModel):
    """
    Модель запроса для обновления JWT токена.

    Атрибуты:
        refresh_token (str): Refresh токен, полученный при аутентификации
    """

    refresh_token: str


class SellerForProductSchema(BaseModel):
    """
    Модель для ответа с данными продавца.
    Используется в ProductPublic схеме.
    """

    id: int = Field(description="Уникальный идентификатор продавца")
    username: str = Field(description="Имя продавца")

    model_config = ConfigDict(from_attributes=True)


class UserForReviewSchema(BaseModel):
    """
    Модель для ответа с данными пользователя в отзывах.

    Используется в ReviewPublic схеме.

    Атрибуты:
        username (str): Имя пользователя, ставившего отзыв
    """

    username: str = Field(description="Имя пользователя")

    model_config = ConfigDict(from_attributes=True)
