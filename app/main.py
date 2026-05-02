from fastapi import FastAPI
from app.domains import routers

app = FastAPI(title="Marketplace", version="1.0")

for router in routers:
    app.include_router(router)
