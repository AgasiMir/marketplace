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
