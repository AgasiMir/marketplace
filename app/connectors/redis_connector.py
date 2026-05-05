import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError, ResponseError
from app.decorators.retry import retry
from app.middlewares.log import logger


class RedisManager:
    def __init__(self, host: str, port: int):
        self.port = port
        self.host = host
        self.redis = None

    @retry(exceptions=(ConnectionError, TimeoutError, ResponseError))
    async def connect(self):
        logger.info(
            f"Начинаю подключение к Redis host={self.host}, port={self.port}..."
        )
        self.redis = await redis.Redis(port=self.port, host=self.host)
        await self.redis.ping()
        logger.info(f"Успешное подключение к Redis host={self.host}, port={self.port}")

    @retry(exceptions=(ConnectionError, TimeoutError, ResponseError))
    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    @retry(exceptions=(ConnectionError, TimeoutError, ResponseError))
    async def get(self, key: str):
        return await self.redis.get(key)

    @retry(exceptions=(ConnectionError, TimeoutError, ResponseError))
    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
