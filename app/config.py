from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: Literal["DEV", "TEST", "PROD"] = "DEV"

    DB_DRIVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str

    SECRET_KEY: str
    ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int

    GF_SECURITY_ADMIN_USER: str
    GF_SECURITY_ADMIN_PASSWORD: str

    # Максимальное количество товаров в избранном
    FAVORITES_MAX_ITEMS: int = 100

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_PORT: int
    RABBITMQ_DEFAULT_HOST: str

    MailDEV_HOST: str

    authentication_backend_secret_key: str

    @property
    def RABBITMQ_URL(self):
        url = f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_DEFAULT_HOST}:{self.RABBITMQ_DEFAULT_PORT}/"
        return url

    @property
    def DB_URL(self):
        url = f"{self.DB_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        return url

    model_config = SettingsConfigDict(env_file=[".env.test"])


settings = Settings()
