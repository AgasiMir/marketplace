from fastapi import APIRouter, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from app.domains.dependencies import DBDep


router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Эндпойнт для проверки работоспособности сервиса",
)
async def health():
    return {"status": "ok"}


@router.get(
    "/check-db",
    status_code=status.HTTP_200_OK,
    summary="Check database",
    description="Проверка подключения к базе данных",
)
async def check_db(db: DBDep):
    version = await db.session.execute(text("SELECT version()"))
    return {"version": version.scalar()}


@router.get("/metrics")
async def get_metrics():
    """
    Эндпоинт для сбора метрик Prometheus.
    Доступ: GET /metrics
    Content-Type: text/plain
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
