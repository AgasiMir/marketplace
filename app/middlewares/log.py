import time
import json
from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


logger.add(
    sink="logs/log.info",
    rotation="10240 KB",
    compression="zip",
    enqueue=True,
    colorize=False,
    serialize=True,
    level="INFO",
    retention="30 days",
)


async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid4())
    request.state.request_id = request_id

    # Не логируем healthcheck'и
    if request.url.path == "/health":
        return await call_next(request)

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        log_data = {
            "event": "request",
            "request_id": request_id,
            # URL может быть сложным объектом, лучше преобразовать в строку
            "request_path": str(request.url.path),
            "method": request.method,
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "client_ip": request.client.host if request.client else None,
            "user_agent": (request.headers.get("user-agent") or "")[:500],
        }

        # Логируем с соответствующим уровнем
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

    except Exception as ex:
        process_time = (time.time() - start_time) * 1000

        log_data = {
            "event": "request_error",
            "request_id": request_id,
            # URL может быть сложным объектом, лучше преобразовать в строку
            "request_path": str(request.url.path),
            "method": request.method,
            "error_type": type(ex).__name__,
            "error_message": str(ex),
            "process_time_ms": round(process_time, 2),
            "client_ip": request.client.host if request.client else None,
            "user_agent": (request.headers.get("user-agent") or "")[:500],
        }
        logger.opt(exception=ex).error(json.dumps(log_data))

        response = JSONResponse(
            content={"success": False, "detail": "Internal server error"},
            status_code=500,
        )

    return response
