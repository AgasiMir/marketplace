from app.domains.categories.repository import CategoryRepository
from app.domains.users.repository import UserRepository
from app.domains.products.repository import ProductRepository


class DBManager:
    """Менеджер базы данных, реализующий паттерн Unit of Work.

    Управляет жизненным циклом сессии базы данных и предоставляет доступ
    к репозиториям для работы с различными сущностями (кошельки, пользователи, операции).
    Гарантирует атомарность операций через автоматическое управление транзакциями.

    Атрибуты:
        wallets (WalletRepository): Репозиторий для работы с кошельками
        users (UserRepository): Репозиторий для работы с пользователями
        operations (OperationRepository): Репозиторий для работы с операциями
    """

    def __init__(self, session_factory):
        """Инициализирует менеджер базы данных.

        Args:
            session_factory: Фабрика для создания сессий SQLAlchemy.
        """

        self.session_factory = session_factory

    async def __aenter__(self):
        """Асинхронный контекстный менеджер: создает сессию и репозитории.

        Создает новую сессию и инициализирует все репозитории (wallets, users, operations)
        с этой сессией, обеспечивая единую точку доступа к данным.

        Returns:
            DBManager: Экземпляр менеджера базы данных.
        """

        self.session = self.session_factory()

        self.categories = CategoryRepository(self.session)
        self.users = UserRepository(self.session)
        self.products = ProductRepository(self.session)

        return self

    async def __aexit__(self, exc_type, *args):
        """Асинхронный контекстный менеджер: завершает сессию.

        Автоматически фиксирует транзакцию при отсутствии исключений
        или откатывает при их наличии. В любом случае закрывает сессию.

        Args:
            exc_type: Тип исключения, если возникло, иначе None.
            *args: Дополнительные аргументы исключения.
        """

        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

    async def commit(self):
        """Фиксирует текущую транзакцию в базе данных.

        Сохраняет все накопленные изменения в базе данных.
        """

        await self.session.commit()

    async def rollback(self):
        """Откатывает текущую транзакцию.

        Отменяет все накопленные изменения с момента начала транзакции.
        """

        await self.session.rollback()

    def add(self, obj):
        """Добавляет объект в сессию для последующего сохранения.

        Объект будет сохранен в базе данных при следующем вызове commit().

        Args:
            obj: Объект модели SQLAlchemy для добавления в сессию.
        """

        self.session.add(obj)

    async def flush(self):
        """Отправляет все накопленные изменения в базу данных без фиксации транзакции.

        Позволяет получить ID для новых объектов до фиксации транзакции.
        """

        await self.session.flush()
