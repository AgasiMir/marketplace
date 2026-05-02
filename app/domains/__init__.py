from .categories.routers import router as categories_router


from .health import router as health_router

routers = [
    categories_router,
    health_router,
]
