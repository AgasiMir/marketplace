import time
from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


logger.add(
    sink="logs/logs.log",
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

    if request.url.path == "/health":
        return await call_next(request)

    try:
        response = await call_next(request)
    except Exception as ex:
        process_time = (time.time() - start_time) * 1000
        logger.bind(request_id=request_id).opt(exception=ex).error(
            "Unhandled exception"
        )
        return JSONResponse(
            content={"success": False, "detail": "Internal server error"},
            status_code=500,
        )

    process_time = (time.time() - start_time) * 1000
    log_data = {
        "event": "request",
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "process_time_ms": round(process_time, 2),
        "client_ip": request.client.host if request.client else None,
        "user_agent": (request.headers.get("user-agent") or "")[:500],
    }

    if response.status_code >= 500:
        logger.error(log_data)
    elif response.status_code >= 400:
        logger.warning(log_data)
    else:
        logger.info(log_data)

    return response
