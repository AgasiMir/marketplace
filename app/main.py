from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.admin.views import CategoryAdmin, ProductAdmin, ReviewAdmin, UserAdmin
from app.init import redis_manager

from app.domains import routers
from app.middlewares.cache_middleware import dispatch
from app.middlewares.log import log_requests
from app.middlewares.metrics_middleware import metrics_middleware

from app.core.database import async_engine
from sqladmin import Admin
from app.admin.auth import authentication_backend


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan, title="Marketplace", version="1.0")


# app.middleware("http")(log_requests)
app.middleware("http")(dispatch)
app.middleware("http")(metrics_middleware)

for router in routers:
    app.include_router(router)


admin = Admin(
    app,
    async_engine,
    title="Панель Администратора",
    authentication_backend=authentication_backend,
)

admin.add_view(UserAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(ProductAdmin)
admin.add_view(ReviewAdmin)
