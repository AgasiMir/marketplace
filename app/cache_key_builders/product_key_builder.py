from fastapi import Request


def product_key_builder(
    func,
    namespace: str = "",
    request: Request | None = None,
    response=None,
    *args,
    **kwargs,
):
    """
    Генерирует предсказуемый ключ вида:
    fastapi-cache:product:<product_id>:user:<user_id>
    """

    data = kwargs.get("kwargs")
    user = data.get("current_user")
    user_id = user.id if user else None
    product_id = data.get("product_id")

    return f"{namespace}:{product_id}:user:{user_id}"
