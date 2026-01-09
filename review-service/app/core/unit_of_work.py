from sqlalchemy.ext.asyncio import AsyncSession
from shared import get_logger

from app.domain.interfaces.unit_of_work import IUnitOfWork

logger = get_logger(__name__)


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

    async def __aenter__(self) -> IUnitOfWork:
        """Вход в контекстный менеджер"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Выход из контекстного менеджера.

        Автоматически коммитит при успехе или откатывает при ошибке.
        """
        if exc_type is None:
            await self.commit()
            logger.debug("Transaction committed successfully")
        else:
            await self.rollback()
            logger.warning(f"Transaction rolled back due to error: {exc_val}", exc_info=True)

