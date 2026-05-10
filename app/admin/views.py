from sqladmin import ModelView
from app.models import User, Category, Product, Review


from app.auth import hash_password


class UserAdmin(ModelView, model=User):
    """
    Административный интерфейс для управления пользователями.

    Наследуется от sqladmin.ModelView, предоставляет CRUD-операции
    для модели User с кастомизацией отображения и поведения.


    Методы:
        on_model_change: Хэширует пароль при создании нового пользователя.
    """

    # Permissions
    can_create = True
    can_delete = False
    # Metadata
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    # List page
    column_list = [
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.role,
        User.email,
    ]
    column_searchable_list = [User.username, User.first_name, User.last_name]
    column_sortable_list = [User.username, User.first_name, User.last_name]

    column_formatters = {User.username: lambda m, a: m.username[:20] + "..."}
    column_formatters = {User.first_name: lambda m, a: m.first_name[:20] + "..."}
    column_formatters = {User.last_name: lambda m, a: m.last_name[:20] + "..."}
    # Details page
    column_details_exclude_list = [User.password]
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
    # Form options
    form_edit_rules = ["is_active", "role"]
    form_create_rules = [
        "first_name",
        "last_name",
        "username",
        "email",
        "password",
        "is_active",
        "role",
    ]

    async def on_model_change(self, data, model, is_created, request) -> None:
        if is_created:
            # Hash the password before saving into DB !
            data["password"] = hash_password(data["password"])


class CategoryAdmin(ModelView, model=Category):
    """
    Административный интерфейс для управления категориями товаров.

    Наследуется от sqladmin.ModelView, предоставляет CRUD-операции
    для модели Category с поддержкой иерархии (родительские/дочерние категории).
    """

    # Permissions
    can_create = True
    can_delete = False
    can_edit = True
    # Metadata
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"
    # List page
    column_list = [
        Category.id,
        Category.name,
        Category.parent,
        Category.children,
    ]
    column_searchable_list = [Category.name]
    column_sortable_list = [
        Category.id,
        Category.name,
    ]
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
    # Form options
    form_edit_rules = [
        "is_active",
        "name",
    ]
    form_create_rules = ["name", "parent", "is_active"]


class ProductAdmin(ModelView, model=Product):
    """
    Административный интерфейс для управления продуктами (товарами).

    Наследуется от sqladmin.ModelView, предоставляет ограниченные CRUD-операции
    для модели Product (создание и удаление запрещены, только просмотр и редактирование).

    """

    # Permissions
    can_create = False
    can_delete = False
    can_edit = True
    # Metadata
    name = "Продукт"
    name_plural = "Продукты"
    icon = "fa-solid fa-cart-plus"
    # List page
    column_list = [
        "seller.username",
        Product.name,
        Product.price,
        Product.description,
        Product.stock,
        Product.rating,
    ]
    column_searchable_list = [Product.name]
    column_sortable_list = [Product.name, Product.price, Product.stock, Product.rating]
    column_formatters = {
        Product.description: lambda m, a: (
            m.description[:20] + "..." if m.description else m.description
        )
    }
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
    # Form options
    form_edit_rules = ["is_active"]


class ReviewAdmin(ModelView, model=Review):
    """
    Административный интерфейс для управления отзывами на продукты.

    Наследуется от sqladmin.ModelView, предоставляет ограниченные CRUD-операции
    для модели Review (создание и удаление запрещены, только просмотр и редактирование).

    """

    # Permissions
    can_create = False
    can_delete = False
    can_edit = True
    # Metadata
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-thumbs-up"
    # List page
    column_list = ["user.username", "product.name", Review.comment, Review.grade]
    column_sortable_list = [Review.grade]
    column_formatters = {
        Review.comment: lambda m, a: m.comment[:20] + "..." if m.comment else m.comment
    }
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
    # Form options
    form_edit_rules = ["is_active"]
