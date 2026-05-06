from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from enum import StrEnum, auto
from app.auth import hash_password


class UserRoleCreate(StrEnum):
    buyer = auto()
    seller = auto()


class UserPublic(BaseModel):
    id: int = Field(description="Уникальный идентификатор пользователя")
    first_name: str = Field(description="Имя пользователя")
    last_name: str = Field(description="Фамилия пользователя")
    username: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Email пользователя")
    role: str = Field(description="Роль пользователя")
    is_active: bool = Field(description="Активен ли пользователь")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
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
    refresh_token: str


class SellerForProductSchema(BaseModel):
    """
    Модель для ответа с данными продавца.
    Используется в Product GET-запросах.
    """

    id: int = Field(description="Уникальный идентификатор продавца")
    username: str = Field(description="Имя продавца")

    model_config = ConfigDict(from_attributes=True)
