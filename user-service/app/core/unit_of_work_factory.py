from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.interfaces.unit_of_work import IUnitOfWork, IUnitOfWorkFactory


class UnitOfWorkFactory:
    """Фабрика для создания экземпляров UnitOfWork
    
    Реализация IUnitOfWorkFactory для SQLAlchemy
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация фабрики

        Args:
            session: Асинхронная сессия базы данных
        """
        self.session = session

    def create(self) -> IUnitOfWork:
        """Создает новый экземпляр UnitOfWork"""
        return UnitOfWork(self.session)
