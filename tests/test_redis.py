import pytest
from redis import Redis

from app.connectors.redis_connector import RedisManager
from unittest.mock import AsyncMock, patch
from redis.exceptions import ConnectionError


@pytest.fixture
def mock_redis_client():
    """Фикстура для мока асинхронного клиента Redis."""
    client = AsyncMock(spec=Redis)
    client.ping = AsyncMock()
    client.set = AsyncMock()
    client.get = AsyncMock(return_value=b"test_value")
    client.delete = AsyncMock()
    client.scan_iter = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def redis_manager(mock_redis_client):
    """Фикстура для экземпляра RedisManager с замоканным redis.Redis."""
    with patch(
        "app.connectors.redis_connector.redis.Redis", return_value=mock_redis_client
    ):
        manager = RedisManager(host="localhost", port=6379)
        # Принудительно подставляем мок, чтобы избежать вызова connect()
        manager.redis = mock_redis_client
        yield manager


@pytest.mark.asyncio
async def test_set_without_expire(redis_manager, mock_redis_client):
    """Тест установки значения без времени жизни."""
    await redis_manager.set("key", "value")
    mock_redis_client.set.assert_awaited_once_with("key", "value")


@pytest.mark.asyncio
async def test_set_with_expire(redis_manager, mock_redis_client):
    """Тест установки значения с временем жизни."""
    await redis_manager.set("key", "value", expire=10)
    mock_redis_client.set.assert_awaited_once_with("key", "value", ex=10)


@pytest.mark.asyncio
async def test_get(redis_manager, mock_redis_client):
    """Тест получения значения."""
    result = await redis_manager.get("key")
    mock_redis_client.get.assert_awaited_once_with("key")
    assert result == b"test_value"


@pytest.mark.asyncio
async def test_delete(redis_manager, mock_redis_client):
    """Тест удаления одного ключа."""
    await redis_manager.delete("key")
    mock_redis_client.delete.assert_awaited_once_with("key")


@pytest.mark.asyncio
async def test_delete_by_pattern_redis_not_connected():
    """Тест удаления по паттерну при отсутствии соединения."""
    manager = RedisManager(host="localhost", port=6379)
    manager.redis = None
    with pytest.raises(ConnectionError, match="Redis не подключен"):
        await manager.delete_by_pattern("pattern")


@pytest.mark.asyncio
async def test_close(redis_manager, mock_redis_client):
    """Тест закрытия соединения."""
    await redis_manager.close()
    mock_redis_client.close.assert_awaited_once()
    assert redis_manager.redis is None


@pytest.mark.asyncio
async def test_close_already_closed(redis_manager, mock_redis_client):
    """Повторный вызов close не должен вызывать ошибку."""
    await redis_manager.close()
    mock_redis_client.close.assert_awaited_once()
    await redis_manager.close()  # второй вызов, redis уже None
    # close больше не вызывается, исключений нет
    assert mock_redis_client.close.await_count == 1
