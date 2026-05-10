# ruff: noqa: E402, F401, F403

import pytest
from typing import AsyncGenerator
from unittest import mock

import pytest_asyncio

from app.auth import hash_password

# Мок для fastapi_cache - отключает кэширование в тестах
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

# Мок для fastapi_limiter - отключает ограничение скорости в тестах
# RateLimiter заменяется на функцию, которая возвращает lambda: None,
# что удовлетворяет интерфейсу Depends и пропускает лимитер
mock.patch(
    "fastapi_limiter.depends.RateLimiter", lambda *args, **kwargs: lambda: None
).start()

# Мок для redis_manager.delete_by_pattern - отключает вызовы Redis в тестах
mock.patch(
    "app.init.redis_manager.delete_by_pattern", mock.AsyncMock(return_value=None)
).start()

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.config import settings
from app.domains.dependencies import get_db
from app.core.database import Base, engine_null_pull, async_session_null_pool
from app.models import Category, User, Product, Favorite, Review
from app.uow.uow import DBManager


@pytest.fixture(autouse=True, scope="session")
def check_test_mode():
    """
    Фикстура безопасности, автоматически запускаемая перед началом тестовой сессии.

    Назначение:
        Гарантирует, что тесты запускаются исключительно в среде 'TEST'.
        Предотвращает случайное выполнение интеграционных или функциональных тестов
        в рабочих (prod) или промежуточных (staging) окружениях, где это может привести
        к потере или повреждению реальных данных.

    Поведение:
        - Автоматически вызывается один раз при старте тестовой сессии (autouse=True).
        - Имеет область видимости 'session' — выполняется до загрузки других фикстур.
        - Проверяет значение `settings.ENVIRONMENT`.
        - Если среда не равна 'TEST', тесты немедленно останавливаются с ошибкой утверждения.

    Пример ожидаемой настройки:
        # settings.py
        ENVIRONMENT = "TEST"

    Почему это важно:
        - Защищает production-базы данных и внешние API от побочных эффектов тестов.
        - Обеспечивает детерминированность тестовой среды.
        - Является частью стратегии безопасного тестирования.

    Примечание:
        Убедитесь, что переменная окружения (например, ENVIRONMENT) установлена в 'TEST'
        перед запуском тестов, иначе выполнение будет прервано.
    """

    assert settings.ENVIRONMENT == "TEST"


async def get_db_null_pull():
    async with DBManager(session_factory=async_session_null_pool) as db:
        yield db


app.dependency_overrides[get_db] = get_db_null_pull


@pytest.fixture
async def db():
    async for db in get_db_null_pull():
        yield db


@pytest.fixture(autouse=True)
async def setup_database(check_test_mode):
    """
    Фикстура для автоматической инициализации тестовой базы данных перед каждым тестом.

    Назначение:
        - Полностью сбрасывает схему базы данных: удаляет все таблицы и создаёт их заново.
        - Обеспечивает чистое и предсказуемое состояние БД перед выполнением каждого теста.
        - Предотвращает влияние одного теста на другой за счёт изоляции данных.

    Зависимости:
        check_test_mode: Убеждается, что тесты запускаются только в безопасном окружении 'TEST'.
                         Эта фикстура выполняется первой благодаря автозапуску и области видимости.

    Поведение:
        - Автоматически вызывается перед каждым тестом (autouse=True, scope="function" по умолчанию).
        - Использует `engine_null_pull` — специальный движок без пула соединений, подходящий для DDL-операций.
        - Выполняет:
            1. DROP TABLE IF EXISTS — удаляет все существующие таблицы.
            2. CREATE TABLE IF NOT EXISTS — создаёт таблицы согласно метаданным `Base`.

    Используется в:
        Интеграционных и функциональных тестах, где требуется работа с реальной (обычно SQLite или тестовой PostgreSQL) БД.

    Почему это важно:
        - Гарантирует, что каждый тест начинается с пустой базы, независимо от результата предыдущего.
        - Устраняет "фоновые" данные, которые могут повлиять на результат теста.
        - Поддерживает воспроизводимость и надёжность тестовой среды.

    Примечания:
        - Убедитесь, что `Base` импортирована из актуального модуля ORM и содержит все модели.
        - `engine_null_pull` должен быть сконфигурирован отдельно (например, через `create_async_engine(url, poolclass=NullPool)`).
        - Не используйте эту фикстуру с production-движком — только с тестовой БД.

    Внимание:
        Так как фикстура имеет autouse=True, она применяется ко всем тестам в сессии.
        Если нужно исключить очистку БД в каком-то тесте — пересмотрите архитектуру или используйте отдельную метку.
    """

    async with engine_null_pull.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для создания асинхронного HTTP-клиента, интегрированного с FastAPI-приложением.

    Назначение:
        Предоставляет экземпляр `httpx.AsyncClient`, настроенный для тестирования API
        без необходимости запуска реального сервера. Использует ASGI-транспорт для прямого
        взаимодействия с приложением (app) на уровне Python.

    Особенности:
        - Работает на уровне ASGI: все запросы обрабатываются напрямую через FastAPI-приложение.
        - Не требует открытия портов или сетевого соединения — идеально подходит для CI/CD.
        - Имеет область видимости 'session' — создаётся один раз за сессию тестирования.
        - Автоматически управляет жизненным циклом клиента (через `async with`).

    Параметры клиента:
        transport = ASGITransport(app=app)
            — Перехватывает HTTP-запросы и направляет их напрямую в приложение FastAPI.
        base_url = "http://test"
            — Базовый URL для всех запросов; используется только для разрешения относительных путей.
            Может быть любым (не влияет на производительность), так как запросы не уходят в сеть.

    Пример использования:
        async def test_read_root(async_client):
            response = await async_client.get("/api/v1/users")
            assert response.status_code == 200

    Возвращаемое значение:
        AsyncGenerator[AsyncClient, None]:
            Клиент, доступный через `yield`, автоматически закрывается после завершения сессии.

    Замечания:
        - Убедитесь, что переменная `app` (экземпляр FastAPI) импортирована корректно.
        - Подходит для интеграционных тестов маршрутов, зависимостей, авторизации и валидации.
        - Не эмулирует задержки сети — поведение быстрее и детерминированнее, чем реальный клиент.

    Альтернативы:
        Для тестов, где важно поведение реальной сети, используйте клиент с реальным transport,
        но в большинстве случаев эта фикстура предпочтительна благодаря скорости и изоляции.
    """

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def register_buyer(async_client):
    """
    Фикстура для регистрации тестового пользователя с ролью "buyer".

    Назначение:
        Автоматически создаёт нового покупателя через API перед выполнением теста.
        Обеспечивает наличие преднастроенного пользователя-покупателя для тестов,
        требующих аутентифицированного доступа или операций от имени покупателя.

    Поведение:
        - Отправляет POST-запрос на эндпоинт `/users` с тестовыми данными.
        - Проверяет, что сервер возвращает статус 201 (Created).
        - При неудаче — прерывает тест с описанием ошибки из тела ответа.

    Данные пользователя:
        - Имя: John
        - Фамилия: Doe
        - Имя пользователя: JD_buyer
        - Email: buyer@example.com
        - Пароль: 1234abcd
        - Роль: buyer

    Зависимости:
        - async_client: Асинхронный HTTP-клиент для взаимодействия с приложением.

    Используется в:
        - authenticated_buyer: Для последующей аутентификации и получения токена.
        - Тестах, требующих наличия зарегистрированного покупателя.

    Примечания:
        - Фикстура имеет область видимости 'function' — создаёт нового пользователя для каждого теста.
        - Использует `assert` для валидации ответа, что останавливает тест при сбое регистрации.
        - Убедитесь, что эндпоинт `/users` и валидация полей работают корректно.
    """

    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD_buyer",
        "email": "buyer@example.com",
        "password": "1234abcd",
        "role": "buyer",
    }
    response = await async_client.post(
        "/users",
        json=data,
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"


@pytest.fixture(scope="function")
async def authenticated_buyer(register_buyer, async_client):

    response = await async_client.post(
        "/users/login",
        data={"username": "JD_buyer", "password": "1234abcd"},
    )

    assert response.status_code == 200, f"Failed to get token: {response.text}"
    token = response.json().get("access_token")

    assert token is not None, "Token is missing in response"
    async_client.headers["Authorization"] = f"Bearer {token}"
    yield async_client


@pytest.fixture(scope="function")
async def register_seller(async_client):
    """
    Фикстура для регистрации тестового пользователя с ролью "seller".

    Назначение:
        Автоматически создаёт нового продавца через API перед выполнением теста.
        Обеспечивает наличие преднастроенного пользователя-продавца для тестов,
        требующих аутентифицированного доступа или операций от имени продавца.

    Поведение:
        - Отправляет POST-запрос на эндпоинт `/users` с тестовыми данными.
        - Проверяет, что сервер возвращает статус 201 (Created).
        - При неудаче — прерывает тест с описанием ошибки из тела ответа.

    Данные пользователя:
        - Имя: John
        - Фамилия: Doe
        - Имя пользователя: JD_seller
        - Email: seller@example.com
        - Пароль: 1234abcd
        - Роль: seller

    Зависимости:
        - async_client: Асинхронный HTTP-клиент для взаимодействия с приложением.

    Используется в:
        - authenticated_buyer: Для последующей аутентификации и получения токена.
        - Тестах, требующих наличия зарегистрированного продавца.

    Примечания:
        - Фикстура имеет область видимости 'function' — создаёт нового пользователя для каждого теста.
        - Использует `assert` для валидации ответа, что останавливает тест при сбое регистрации.
        - Убедитесь, что эндпоинт `/users` и валидация полей работают корректно.
    """

    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "JD_seller",
        "email": "seller@example.com",
        "password": "1234abcd",
        "role": "seller",
    }
    response = await async_client.post(
        "/users",
        json=data,
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"


@pytest.fixture(scope="function")
async def authenticated_seller(register_seller, async_client):

    response = await async_client.post(
        "/users/login",
        data={"username": "JD_seller", "password": "1234abcd"},
    )

    assert response.status_code == 200, f"Failed to get token: {response.text}"
    token = response.json().get("access_token")

    assert token is not None, "Token is missing in response"
    async_client.headers["Authorization"] = f"Bearer {token}"
    yield async_client


@pytest.fixture()
async def register_admin(db: DBManager):
    """
    Фикстура для регистрации тестового администратора с ролью "admin".

    Назначение:
        Автоматически создаёт нового администратора через API перед выполнением теста.
        Обеспечивает наличие преднастроенного пользователя-администратора для тестов,
        требующих аутентифицированного доступа или операций от имени администратора.

    Поведение:
        - Отправляет POST-запрос на эндпоинт `/users` с тестовыми данными.
        - Проверяет, что сервер возвращает статус 201 (Created).
        - При неудаче — прерывает тест с описанием ошибки из тела ответа.

    Данные пользователя:
        - Имя: Jane
        - Фамилия: Doe
        - Имя пользователя: Ja_Do
        - Email: user@example.org
        - Пароль: 1234abcd
        - Роль: admin

    Зависимости:
        - async_client: Асинхронный HTTP-клиент для взаимодействия с приложением.

    Используется в:
        - authenticated_buyer: Для последующей аутентификации и получения токена.
        - Тестах, требующих наличия зарегистрированного администратора.

    Примечания:
        - Фикстура имеет область видимости 'function' — создаёт нового пользователя для каждого теста.
        - Использует `assert` для валидации ответа, что останавливает тест при сбое регистрации.
        - Убедитесь, что эндпоинт `/users` и валидация полей работают корректно.
    """

    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "username": "Ja_Do",
        "email": "user@example.org",
        "password": hash_password("1234abcd"),
        "role": "admin",
    }

    admin_user = User(**data)
    db.add(admin_user)
    await db.commit()


@pytest.fixture(scope="function")
async def authenticated_admin(register_admin, async_client):

    response = await async_client.post(
        "/users/login",
        data={"username": "Ja_Do", "password": "1234abcd"},
    )

    assert response.status_code == 200, f"Failed to get token: {response.text}"
    token = response.json().get("access_token")

    assert token is not None, "Token is missing in response"
    async_client.headers["Authorization"] = f"Bearer {token}"
    yield async_client


@pytest.fixture
async def category_user_product(db: DBManager):
    """
    Фикстура для создания связанных тестовых сущностей: категории, пользователя-продавца и товара.

    Назначение:
        Подготавливает преднастроенную тестовую среду с полными данными,
        необходимыми для интеграционных тестов, связанных с товарами, категориями и продавцами.
        Создаёт одну категорию, одного пользователя со статусом продавца и один товар,
        принадлежащий этой категории и продавцу.

    Поведение:
        - Создаёт объект Category с именем "Test Category".
        - Создаёт объект User с ролью "seller" и тестовыми данными.
        - Создаёт объект Product, связывая его с созданной категорией и продавцом.
        - Сохраняет все объекты в базу данных через переданный экземпляр DBManager (db).
        - Проверяет корректность работы методов __repr__ у всех моделей.
        - Возвращает кортеж (category, user, product) для использования в тестах.

    Возвращаемые данные:
        - category: экземпляр Category, созданный в БД.
        - user: экземпляр User (продавец), созданный в БД.
        - product: экземпляр Product, созданный в БД, связанный с category и user.

    Зависимости:
        - db: Фикстура, предоставляющая экземпляр DBManager для работы с базой данных.

    Используется в:
        - Тестах, требующих наличие товара с привязкой к категории и продавцу.
        - Интеграционных тестах маршрутов создания, получения, обновления и удаления товаров.
        - Тестах фильтрации и поиска по категориям и продавцам.

    Примечания:
        - Фикстура использует синхронную модель создания объектов через ORM.
        - Убедитесь, что модели Category, User и Product импортированы и корректно определены.
        - Зависит от корректной работы методов add и commit у DBManager.
        - Тестовые данные (имена, email и т.д.) фиксированы и могут быть использованы в assert.
    """

    category_data = {"name": "Test Category"}
    user_data = {
        "first_name": "Test_Name",
        "last_name": "Test_Last_Name",
        "username": "Test_User",
        "email": "testuser@example.com",
        "password": hash_password("1234abcd"),
        "role": "seller",
    }

    category = Category(**category_data)
    db.add(category)
    await db.commit()

    user = User(**user_data)
    db.add(user)
    await db.commit()

    product_data = {
        "name": "Test Product",
        "description": None,
        "price": 10.00,
        "image_url": "",
        "stock": 10,
        "category_id": category.id,
        "seller_id": user.id,
    }

    product = Product(**product_data)
    db.add(product)
    await db.commit()

    assert category.__repr__() == category.name
    assert user.__repr__() == user.username
    assert product.__repr__() == f"{product.name}, {product.price}"

    return category, user, product
