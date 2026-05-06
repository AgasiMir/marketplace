import pytest
from unittest.mock import AsyncMock, patch
from app.connectors.redis_connector import RedisManager


# Мокаем логгер, чтобы не засорять вывод
@pytest.fixture(autouse=True)
def mock_logger():
    with patch("app.connectors.redis_connector.logger") as mock:
        yield mock


# Тестируем RedisManager
class TestRedisManager:
    @pytest.fixture
    def redis_manager(self):
        """
        Создаем экземпляр RedisManager с тестовыми параметрами
        """
        return RedisManager(host="localhost", port=6379)

    @patch("app.connectors.redis_connector.redis.Redis")
    async def test_connect_success(self, mock_redis, redis_manager):
        # Подготовка: мокаем ping и возвращаем успех
        mock_instance = AsyncMock()
        mock_instance.ping.return_value = "PONG"
        # Делаем mock_redis вызываемым и возвращающим mock_instance
        mock_redis.return_value = mock_instance

        # Также делаем mock_redis awaitable, чтобы await redis.Redis(...) работал
        # Для этого используем side_effect, который возвращает mock_instance
        # и делает mock_redis вызываемым как асинхронная функция
        async def async_constructor(*args, **kwargs):
            return mock_instance

        mock_redis.side_effect = async_constructor

        # Действие
        await redis_manager.connect()

        # Проверки
        mock_redis.assert_called_once_with(port=6379, host="localhost")
        mock_instance.ping.assert_awaited_once()
        # Проверяем вызовы логгера через мок
        from app.connectors.redis_connector import logger as mock_log

        mock_log.info.assert_any_call(
            "Начинаю подключение к Redis host=localhost, port=6379..."
        )
        mock_log.info.assert_any_call(
            "Успешное подключение к Redis host=localhost, port=6379"
        )

    @patch("app.connectors.redis_connector.redis.Redis")
    async def skip_test_connect_failure(self, mock_redis, redis_manager):
        # Подготовка: эмулируем ошибку при подключении
        mock_redis.side_effect = Exception("Connection failed")

        # Действие и проверка исключения
        with pytest.raises(Exception, match="Connection failed"):
            await redis_manager.connect()

        # Проверяем вызов логгера ошибки
        from app.connectors.redis_connector import logger as mock_log

        mock_log.error.assert_called_once()
        error_msg = mock_log.error.call_args[0][0]
        assert "Ошибка подключения к Redis" in error_msg
        assert "Connection failed" in error_msg

    async def test_set_key_without_expire(self, redis_manager):
        # Подготовка
        redis_manager.redis = AsyncMock()

        # Действие
        await redis_manager.set("test_key", "test_value")

        # Проверка
        redis_manager.redis.set.assert_awaited_once_with("test_key", "test_value")

    async def test_set_key_with_expire(self, redis_manager):
        # Подготовка
        redis_manager.redis = AsyncMock()

        # Действие
        await redis_manager.set("test_key", "test_value", expire=60)

        # Проверка
        redis_manager.redis.set.assert_awaited_once_with(
            "test_key", "test_value", ex=60
        )

    async def test_get_key(self, redis_manager):
        # Подготовка
        redis_manager.redis = AsyncMock()
        redis_manager.redis.get.return_value = b"test_value"

        # Действие
        result = await redis_manager.get("test_key")

        # Проверка
        assert result == b"test_value"
        redis_manager.redis.get.assert_awaited_once_with("test_key")

    async def test_delete_key(self, redis_manager):
        # Подготовка
        redis_manager.redis = AsyncMock()

        # Действие
        await redis_manager.delete("test_key")

        # Проверка
        redis_manager.redis.delete.assert_awaited_once_with("test_key")

    async def test_close_connection(self, redis_manager):
        # Подготовка
        mock_redis = AsyncMock()
        redis_manager.redis = mock_redis

        # Действие
        await redis_manager.close()

        # Проверка
        mock_redis.close.assert_awaited_once()
        assert redis_manager.redis is None
