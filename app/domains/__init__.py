from .categories.routers import router as categories_router
from .users.routers import router as users_router
from .products.routers import router as products_router
from .favorites.routers import router as favorites_router

from .health import router as health_router

routers = [
    health_router,
    users_router,
    categories_router,
    products_router,
    favorites_router,
]
