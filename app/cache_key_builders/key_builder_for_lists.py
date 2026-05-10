import hashlib
from fastapi import Request


def key_builder_for_lists(
    func,
    namespace: str = "",
    request: Request | None = None,
    response=None,
    *args,
    **kwargs,
):
    """Строитель ключей кэша для списковых операций.

    Генерирует уникальный ключ кэша на основе функции, пространства имен,
    параметров запроса и текущего пользователя. Используется для кэширования
    результатов функций, возвращающих списки (например, списки товаров, категорий).

    Ключ формируется как MD5 хэш строки, содержащей:
    - Модуль и имя функции
    - Параметры запроса (исключая 'products' и 'current_user')
    - Идентификатор текущего пользователя (если есть)

    Args:
        func (Callable): Функция, для которой строится ключ кэша.
        namespace (str, optional): Пространство имен для группировки ключей.
            По умолчанию пустая строка.
        request (Request | None, optional): Объект запроса FastAPI.
            По умолчанию None.
        response (Any, optional): Объект ответа (не используется в текущей реализации).
            По умолчанию None.
        *args: Произвольные позиционные аргументы (не используются).
        **kwargs: Произвольные ключевые аргументы. Ожидается, что содержат
            ключ "kwargs" с параметрами запроса, включая "current_user".

    Returns:
        str: Ключ кэша в формате "{namespace}:{md5_hash}".

    Examples:
        >>> key_builder_for_lists(
        ...     func=some_function,
        ...     namespace="list_of_products",
        ...     request=request,
        ...     kwargs={"category_id": 1, "current_user": user}
        ... )
        "list_of_products:abc123def456..."
    """

    cache_kw = {}
    data = kwargs.get("kwargs")
    user = data.get("current_user")
    user_id = user.id if user else None

    for key, value in data.items():
        if key not in ["products", "current_user"]:
            cache_kw[key] = value

    cache_kw |= {"user_id": f"{user_id}"}

    cache_key = hashlib.md5(  # noqa: S324
        f"{func.__module__}:{func.__name__}:{cache_kw}".encode()
    ).hexdigest()

    return f"{namespace}:{cache_key}"
