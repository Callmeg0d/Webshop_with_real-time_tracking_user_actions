import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import HTTPException

os.environ["MODE"] = "TEST"

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.config import settings
from tests.fixtures.test_data import get_existing_product_ids

pytest_plugins = ["shared.test_utils.conftest"]


_db_initialized = False


@pytest.fixture(scope="session", autouse=True)
async def _setup_test_db():
    """Создает таблицы один раз на сессию тестов"""
    global _db_initialized
    if not _db_initialized:
        engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        _db_initialized = True


@pytest.fixture(scope="function")
async def test_engine(_setup_test_db):
    """Создает engine для тестовой БД для каждого теста (переиспользует созданные таблицы)"""
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_engine):
    """Создает тестовую сессию БД для каждого теста с транзакционной изоляцией"""
    test_session_maker = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    
    async with test_session_maker() as session:
        await session.execute(text("TRUNCATE TABLE reviews RESTART IDENTITY CASCADE"))
        await session.commit()
        
        yield session

        await session.execute(text("TRUNCATE TABLE reviews RESTART IDENTITY CASCADE"))
        await session.commit()


@pytest.fixture
def mock_user_info(mocker):
    """Фикстура для мока get_user_info - можно переопределить в тестах"""
    async def _mock_get_user_info(user_id: int):
        return {"email": f"user{user_id}@example.com", "name": f"User {user_id}"}
    
    mocker.patch('app.services.review_service.get_user_info', side_effect=_mock_get_user_info)
    return _mock_get_user_info


@pytest.fixture
def mock_users_batch(mocker):
    """Фикстура для мока get_users_batch - можно переопределить в тестах"""
    async def _mock_get_users_batch(user_ids: list[int]):
        return {
            user_id: {"email": f"user{user_id}@example.com", "name": f"User {user_id}"}
            for user_id in user_ids
        }
    
    mocker.patch('app.services.review_service.get_users_batch', side_effect=_mock_get_users_batch)
    return _mock_get_users_batch


@pytest.fixture
def mock_check_product(mocker):
    """Фикстура для мока check_product_exists - можно переопределить в тестах"""
    existing_products = get_existing_product_ids()
    
    async def _mock_check_product(product_id: int) -> int:
        if product_id in existing_products:
            return product_id
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    mocker.patch('app.api.reviews.check_product_exists', side_effect=_mock_check_product)
    return _mock_check_product


@pytest.fixture(scope="function")
async def async_client(test_db_session: AsyncSession, mock_user_info, mock_users_batch, mock_check_product):
    """Создает AsyncClient для тестирования API"""
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
