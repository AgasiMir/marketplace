"""
Middleware для управления кэшированием

Middleware, предотвращающий кэширование ответов браузером,
устанавливая соответствующие HTTP-заголовки:
- Cache-Control: no-cache, no-store, must-revalidate
- Pragma: no-cache
- Expires: 0

Используется в FastAPI для обеспечения актуальности данных.
"""


async def dispatch(request, call_next):
    response = await call_next(request)
    # Добавляем заголовки для предотвращения кэширования браузером
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
