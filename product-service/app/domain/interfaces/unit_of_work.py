from typing import Protocol


class IUnitOfWork(Protocol):
    """Интерфейс для Unit of Work паттерна
    
    Unit of Work управляет транзакциями и обеспечивает атомарность операций
    Используется для координации изменений в репозиториях
    """

    async def commit(self) -> None:
        """Коммитит все изменения в транзакции"""
        ...

    async def rollback(self) -> None:
        """Откатывает все изменения в транзакции"""
        ...

    async def __aenter__(self) -> "IUnitOfWork":
        """Вход в контекстный менеджер"""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера
        
        Автоматически коммитит при успехе или откатывает при ошибке.
        """
        ...


class IUnitOfWorkFactory(Protocol):
    """Фабрика для создания экземпляров IUnitOfWork
    
    Позволяет создавать UnitOfWork без прямой зависимости от инфраструктуры
    """

    def create(self) -> IUnitOfWork:
        """Создает новый экземпляр UnitOfWork"""
        ...
