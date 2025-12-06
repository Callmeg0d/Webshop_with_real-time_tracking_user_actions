from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession


class IUnitOfWork(Protocol):
    """Интерфейс для Unit of Work"""

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...

    async def __aenter__(self) -> "IUnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        ...


class UnitOfWork:
    """
    Unit of Work для управления транзакциями.

    Автоматически коммитит изменения при успешном выполнении
    или откатывает при возникновении исключения.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация Unit of Work.

        Args:
            session: Асинхронная сессия базы данных
        """
        self.session = session

    async def commit(self) -> None:
        """Коммитит все изменения в транзакции"""
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатывает все изменения в транзакции"""
        await self.session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        """Вход в контекстный менеджер"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Выход из контекстного менеджера.

        Автоматически коммитит при успехе или откатывает при ошибке.
        """
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
