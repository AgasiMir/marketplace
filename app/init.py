from app.config import settings
from app.connectors.redis_connector import RedisManager

redis_manager = RedisManager(port=settings.REDIS_PORT, host=settings.REDIS_HOST)
